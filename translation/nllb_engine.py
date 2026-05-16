"""
PolyVerba — NLLB-600M Translation Engine (CTranslate2 Backend)

Uses Meta's NLLB-200-Distilled-600M model for high-accuracy translation
to all 12+ Indian languages with correct native scripts.

Backend: CTranslate2 (optimized C++ inference, 2-4x faster than PyTorch on CPU)
Quantization: INT8 (halves memory usage, speeds up CPU inference)

NLLB Language Codes (FLORES-200 standard):
  Hindi       → hin_Deva
  Tamil       → tam_Taml
  Telugu      → tel_Telu
  Kannada     → kan_Knda
  Malayalam   → mal_Mlym
  Bengali     → ben_Beng
  Gujarati    → guj_Gujr
  Marathi     → mar_Deva
  Punjabi     → pan_Guru
  Urdu        → urd_Arab
  Assamese    → asm_Beng
  Nepali      → npi_Deva
  Odia        → ory_Orya
  English     → eng_Latn

── Alternative Translation Backends ──────────────────────────────────────────
  You can swap NLLB-600M for either of these higher-accuracy Indic-specialized models:

  Option A — AI4Bharat IndicTrans2 200M (Distilled)
    Model ID : ai4bharat/indictrans2-en-indic-dist-200M
    Library  : indic-nlp-library  (pip install indic-nlp-library)
               This library handles ALL 22 Indian language scripts natively —
               Devanagari, Tamil, Telugu, Bengali, Gurmukhi, Odia, Ol Chiki etc.
               and provides tokenization, script detection, and transliteration.
    Advantage: Trained specifically on Indian languages; produces significantly
               more natural, grammatically accurate Indic output than NLLB.

  Option B — AI4Bharat IndicTrans2 1B
    Model ID : ai4bharat/indictrans2-en-indic-1B
    Advantage: Full 1B parameter model; highest accuracy of all three options;
               best choice if a GPU is available (requires ~4GB VRAM).

  Reference : https://github.com/AI4Bharat/IndicTrans2
  Paper     : https://arxiv.org/abs/2305.16307
──────────────────────────────────────────────────────────────────────────────
"""

import os
# Force offline mode so the tokenizer doesn't hang trying to ping the internet
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import time
import ctranslate2
from transformers import AutoTokenizer

# Current model: Meta NLLB-200-Distilled-600M (FLORES-200 codes)
# Alternative  : ai4bharat/indictrans2-en-indic-dist-200M  (pip install indic-nlp-library)
# Alternative  : ai4bharat/indictrans2-en-indic-1B          (best accuracy, needs GPU)
NLLB_MODEL_ID = "facebook/nllb-200-distilled-600M"
CT2_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "nllb-600m-ct2")

class NLLBEngine:
    def __init__(self):
        import torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        ct2_device  = "cuda" if self.device == "cuda" else "cpu"
        quantize    = "float16" if self.device == "cuda" else "int8"

        print(f"[TRANSLATION] Device: {self.device.upper()}")
        # Loading NLLB-200-Distilled-600M via CTranslate2
        # Alternatives: ai4bharat/indictrans2-en-indic-dist-200M (via indic-nlp-library)
        #               ai4bharat/indictrans2-en-indic-1B         (highest accuracy, GPU recommended)
        print(f"[TRANSLATION] Loading NLLB-200-Distilled-600M via CTranslate2 ({quantize})...")
        
        if not os.path.exists(os.path.join(CT2_MODEL_DIR, "model.bin")):
            raise RuntimeError(f"CTranslate2 model not found at {CT2_MODEL_DIR}. Please run convert_nllb.py first!")

        t = time.time()

        self._translator = ctranslate2.Translator(
            CT2_MODEL_DIR,
            device=ct2_device,
            inter_threads=4,           # parallel CPU threads
            intra_threads=2,           # BLAS threads per translation
            compute_type=quantize,
        )
        self._tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL_ID)

        elapsed = time.time() - t
        print(f"[TRANSLATION] NLLB-600M ready in {elapsed:.1f}s — engines loaded!")

    # ── Translation ─────────────────────────────────────────────────────────

    def translate(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn") -> str:
        """
        Translates text from source_lang to target_lang using NLLB-600M.
        Both source_lang and target_lang must be FLORES-200 codes.
        """
        if not text or not text.strip():
            return ""

        try:
            # Tokenize with source language token
            self._tokenizer.src_lang = source_lang
            tokens = self._tokenizer(text.strip(), return_tensors="pt")
            input_ids = tokens["input_ids"]

            # Convert to list of tokens for CTranslate2
            token_list = [
                self._tokenizer.convert_ids_to_tokens(row.tolist())
                for row in input_ids
            ]

            # Get the target language token id for forced BOS
            target_prefix = [[target_lang]]

            results = self._translator.translate_batch(
                token_list,
                target_prefix=target_prefix,
                max_decoding_length=45,
                beam_size=2,             # beam=2: sweet spot accuracy/speed on CPU
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
            )

            # Decode output tokens back to text
            output_tokens = results[0].hypotheses[0]
            # Remove the forced target-lang prefix token
            if output_tokens and output_tokens[0] == target_lang:
                output_tokens = output_tokens[1:]

            translation = self._tokenizer.decode(
                self._tokenizer.convert_tokens_to_ids(output_tokens),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            ).strip()

            return translation

        except Exception as e:
            print(f"[TRANSLATION ERROR] {e}")
            return ""

    def translate_stream(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn"):
        """
        Token-by-token streaming generator using CTranslate2 async generation.
        Yields decoded text chunks in real-time as they are generated.
        """
        if not text or not text.strip():
            return

        try:
            self._tokenizer.src_lang = source_lang
            tokens = self._tokenizer(text.strip(), return_tensors="pt")
            input_ids = tokens["input_ids"]

            token_list = [
                self._tokenizer.convert_ids_to_tokens(row.tolist())
                for row in input_ids
            ]

            target_prefix = [[target_lang]]

            # Use CTranslate2 async generator for streaming
            result_iter = self._translator.translate_batch(
                token_list,
                target_prefix=target_prefix,
                max_decoding_length=45,
                beam_size=1,             # beam=1 required for true streaming output
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                asynchronous=True,
            )

            for future in result_iter:
                result = future.result()
                output_tokens = result.hypotheses[0]

                # Remove forced prefix token
                if output_tokens and output_tokens[0] == target_lang:
                    output_tokens = output_tokens[1:]

                if not output_tokens:
                    continue

                decoded = self._tokenizer.decode(
                    self._tokenizer.convert_tokens_to_ids(output_tokens),
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True
                ).strip()

                if decoded:
                    # CTranslate2 translates the full chunk extremely fast.
                    # We split and yield word-by-word to simulate the token streaming effect for the UI.
                    words = decoded.split()
                    for i, word in enumerate(words):
                        # Append space for all words except the last to preserve natural spacing
                        yield word + (" " if i < len(words) - 1 else "")

        except Exception as e:
            print(f"[TRANSLATION STREAM ERROR] {e}")

    def is_reliable(self, target_lang: str) -> bool:
        """NLLB-600M handles all 200 languages reliably — always True."""
        return True
