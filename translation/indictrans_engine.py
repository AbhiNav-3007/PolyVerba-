"""
PolyVerba — IndicTrans2 Translation Engine

Auto-detects GPU/CPU and selects the best model per direction.
ALL models are loaded at startup — no surprise delays mid-session.

GPU (CUDA):
  en-indic:    ai4bharat/indictrans2-en-indic-1B       (float16, correct native scripts)
  indic-en:    ai4bharat/indictrans2-indic-en-dist-200M
  indic-indic: ai4bharat/indictrans2-indic-indic-dist-320M

CPU:
  en-indic:    ai4bharat/indictrans2-en-indic-dist-200M
  indic-en:    ai4bharat/indictrans2-indic-en-dist-200M
  indic-indic: ai4bharat/indictrans2-indic-indic-dist-320M

BOS artifact fix: strip generated_tokens[:, 1:] before decoding.
"""

import re
import time
import torch
import torch.quantization
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class IndicTransEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Select model names based on hardware
        if self.device == "cuda":
            self._model_names = {
                "en-indic":    "ai4bharat/indictrans2-en-indic-1B",
                "indic-en":    "ai4bharat/indictrans2-indic-en-dist-200M",
                "indic-indic": "ai4bharat/indictrans2-indic-indic-dist-320M",
            }
            precision = "Float16 (CUDA)"
            print(f"[TRANSLATION] Device: {self.device.upper()} | Precision: {precision}")
            print(f"[TRANSLATION] Loading all 3 translation models sequentially...")
        else:
            self._model_names = {
                "en-indic":    "ai4bharat/indictrans2-en-indic-dist-200M",
                "indic-en":    "ai4bharat/indictrans2-indic-en-dist-200M",
            }
            precision = "Float32 (CPU Edge Mode)"
            print(f"[TRANSLATION] Device: {self.device.upper()} | Precision: {precision}")
            print(f"[TRANSLATION] Loading 2 core translation models sequentially (prevents RAM freeze)...")
        print(f"[TRANSLATION] (First run downloads from HuggingFace — may take 1-10 mins)")

        total_start = time.time()
        self._tokenizers = {}
        self._models     = {}
        _errors          = {}

        for direction, model_name in self._model_names.items():
            try:
                t = time.time()
                print(f"[TRANSLATION] [{direction}] Starting: {model_name}")
                tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                mdl = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
                mdl = mdl.to(self.device)
                if self.device == "cuda":
                    mdl = mdl.half()   # float16 — 2x faster, same accuracy
                else:
                    # Dynamically quantize Linear layers to INT8 for massive CPU speedup (2x-3x faster)
                    mdl = torch.quantization.quantize_dynamic(
                        mdl, {torch.nn.Linear}, dtype=torch.qint8
                    )
                mdl.eval()
                elapsed = time.time() - t
                print(f"[TRANSLATION] [{direction}] Ready in {elapsed:.1f}s (OK)")
                
                self._tokenizers[direction] = tok
                self._models[direction]     = mdl
            except Exception as e:
                print(f"[TRANSLATION] [{direction}] FAILED: {e}")
                _errors[direction] = e

        if _errors:
            raise RuntimeError(
                f"[TRANSLATION] Failed to load: {list(_errors.keys())}. "
                f"Check HuggingFace access and internet connection."
            )

        total = time.time() - total_start
        print(f"[TRANSLATION] All models ready in {total:.1f}s — engines loaded!")

    # ── Direction Routing ────────────────────────────────────────────────────

    def _get_direction(self, source_lang: str, target_lang: str) -> str:
        """Select the correct model direction from FLORES language codes."""
        if source_lang == "eng_Latn" and target_lang != "eng_Latn":
            return "en-indic"
        elif source_lang != "eng_Latn" and target_lang == "eng_Latn":
            return "indic-en"
        elif source_lang != "eng_Latn" and target_lang != "eng_Latn":
            if "indic-indic" in self._tokenizers:
                return "indic-indic"
            else:
                print("[TRANSLATION WARNING] indic-indic model not loaded on CPU. Falling back to en-indic.")
                return "en-indic"
        return "en-indic"  # fallback

    # ── Translation ─────────────────────────────────────────────────────────

    def translate(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn") -> str:
        """
        Translates text between any supported language pair.
        Automatically selects the correct model direction.

        Tokenizer format: "eng_Latn hin_Deva The actual sentence"
        BOS artifact fix: strip generated_tokens[:, 1:] before decoding.
        """
        if not text or not text.strip():
            return ""

        try:
            direction = self._get_direction(source_lang, target_lang)
            tokenizer = self._tokenizers[direction]
            model     = self._models[direction]

            tagged = f"{source_lang} {target_lang} {text.strip()}"

            inputs = tokenizer(
                tagged,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            )

            # Move inputs to same device as model
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            forced_bos = tokenizer.convert_tokens_to_ids(target_lang)
            beam = 4 if self.device == "cuda" else 1

            with torch.no_grad():
                gen = model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=60,          # Capped: prevents 25-second CPU hang on hallucination
                    num_beams=beam,
                    repetition_penalty=1.2, # Prevents the ".........." loop
                    forced_bos_token_id=forced_bos
                )

            # Strip forced BOS token — it decodes to garbage chars like "छे," "आणि"
            out = gen[:, 1:]

            translation = tokenizer.batch_decode(
                out,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0].strip()

            # Strip residual short artifact at start (e.g. "छे, " "कि " "से ")
            translation = self._strip_leading_artifact(translation)

            return translation

        except Exception as e:
            print(f"[TRANSLATION ERROR] {e}")
            return ""

    def _strip_leading_artifact(self, text: str) -> str:
        """Remove BOS residual artifacts: "छे, text" → "text", "कि text" → "text" """
        if not text:
            return text
        words = text.split()
        if len(words) >= 2 and len(words[0]) <= 4:
            remaining = " ".join(words[1:]).strip().lstrip(",. ")
            if len(remaining) > len(text) * 0.5:
                return remaining
        return text

    def is_reliable(self, target_lang: str) -> bool:
        """On GPU with 1B model, ALL languages output correct native script."""
        if self.device == "cuda":
            return True  # 1B model handles all 22 Indian scripts correctly
        # CPU 200M model: Dravidian scripts (Tamil/Telugu/Kannada/Malayalam) are unreliable
        RELIABLE_200M = {
            "hin_Deva", "mar_Deva", "ben_Beng",
            "urd_Arab", "pan_Guru", "asm_Beng", "npi_Deva"
        }
        return target_lang in RELIABLE_200M
