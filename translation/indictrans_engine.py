"""
PolyVerba — IndicTrans2 Translation Engine

Fixed tokenizer API: format is "eng_Latn hin_Deva text"
Fixed BOS artifact: strip generated_tokens[:, 1:] before decoding
"""

import re
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Languages with reliable script output from dist-200M model
RELIABLE_LANGS = {
    "hin_Deva",  # Hindi ✅
    "mar_Deva",  # Marathi ✅
    "ben_Beng",  # Bengali ✅
    "urd_Arab",  # Urdu ✅
    "pan_Guru",  # Punjabi ✅
    "asm_Beng",  # Assamese ✅
    "npi_Deva",  # Nepali ✅
}

# Devanagari-script artifact patterns to strip from beginning of translations
_BOS_ARTIFACT = re.compile(
    r'^[\u0900-\u097F\u0D00-\u0D7F\u0980-\u09FF\u0A00-\u0A7F()\u0B00-\u0B7F]*'  # Indian script chars
    r'[^\u0900-\u097F\w]*'   # optional punctuation/space after
)


class IndicTransEngine:
    def __init__(self):
        print("[TRANSLATION] Loading ai4bharat/indictrans2-en-indic-dist-200M...")
        model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
        start = time.time()

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name, trust_remote_code=True
            )
            self.model.eval()
            print(f"[TRANSLATION] Model loaded in {time.time()-start:.1f}s")
            print("[TRANSLATION] Device: CPU (Float32 Edge Mode)")
        except Exception as e:
            print(f"[TRANSLATION ERROR] Failed to load: {e}")
            raise

    def translate(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn") -> str:
        """
        Translates English text → target Indian language.

        Tokenizer format: "eng_Latn hin_Deva The actual sentence"
        BOS artifact fix: strip generated_tokens[:, 1:] before decoding.
        """
        if not text or not text.strip():
            return ""

        try:
            # IndicTransTokenizer._src_tokenize splits first 2 tokens as src/tgt lang
            tagged = f"{source_lang} {target_lang} {text.strip()}"

            inputs = self.tokenizer(
                tagged,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            )

            forced_bos = self.tokenizer.convert_tokens_to_ids(target_lang)

            with torch.no_grad():
                gen = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    forced_bos_token_id=forced_bos
                )

            # Strip forced BOS token — it decodes to garbage chars like "छे," "आणि"
            out = gen[:, 1:]

            translation = self.tokenizer.batch_decode(
                out,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0].strip()

            # Secondary cleanup: strip any residual 1-3 char artifact at the start
            # These look like "छे, " "कि " "से " "और " — short filler words from model
            translation = self._strip_leading_artifact(translation, target_lang)

            return translation

        except Exception as e:
            print(f"[TRANSLATION ERROR] {e}")
            return ""

    def _strip_leading_artifact(self, text: str, target_lang: str) -> str:
        """
        Remove BOS residual artifacts from beginning of translated text.
        Examples: "छे, text" -> "text", "कि text" -> "text", "आणि text" -> "text"
        """
        if not text:
            return text

        # Known artifact patterns: 1-4 char word at start, ends in space/comma/space
        artifact_pattern = re.compile(r'^[\w\u0900-\u0D7F]{1,4}[,\.\s]+')
        words = text.split()

        # Only strip if first "word" is 1-4 chars and rest of text is substantial
        if len(words) >= 2 and len(words[0]) <= 4:
            remaining = " ".join(words[1:]).strip().lstrip(",. ")
            if len(remaining) > len(text) * 0.5:  # remaining is more than half
                return remaining

        return text

    def is_reliable(self, target_lang: str) -> bool:
        """Check if dist-200M produces reliable script for this language."""
        return target_lang in RELIABLE_LANGS
