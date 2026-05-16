"""
PolyVerba — Language Code Mappings (NLLB-200 / FLORES-200 standard)

Maps human-readable language names to FLORES-200 codes used by Meta NLLB-600M.
All codes verified against facebook/nllb-200-distilled-600M tokenizer vocabulary.

NOTE: If switching to AI4Bharat IndicTrans2 (pip install indic-nlp-library),
      the model IDs are:
        ai4bharat/indictrans2-en-indic-dist-200M  (200M distilled, lightweight)
        ai4bharat/indictrans2-en-indic-1B          (1B, highest accuracy)
      IndicTrans2 uses ISO 639 language codes (e.g. 'hin', 'tam', 'tel')
      instead of FLORES-200 codes, so this mapping table will need updating.
      The `indic-nlp-library` package provides script detection, tokenization,
      and transliteration for ALL 22 Indian language scripts natively.
"""

# Display name → FLORES-200 code (for translate() calls)
FLORES_CODES = {
    "Hindi":            "hin_Deva",
    "Marathi":          "mar_Deva",
    "Tamil":            "tam_Taml",
    "Telugu":           "tel_Telu",
    "Kannada":          "kan_Knda",
    "Bengali":          "ben_Beng",
    "Gujarati":         "guj_Gujr",
    "Malayalam":        "mal_Mlym",
    "Punjabi":          "pan_Guru",
    "Odia":             "ory_Orya",
    "Urdu":             "urd_Arab",
    "Assamese":         "asm_Beng",
    "Nepali":           "npi_Deva",
    "English (Latin)":  "eng_Latn",
}

# FLORES code → display name (reverse lookup)
FLORES_TO_NAME = {v: k for k, v in FLORES_CODES.items()}

# Ordered list for the frontend dropdown (English first, rest alphabetical)
LANGUAGE_NAMES = ["English (Latin)"] + sorted(k for k in FLORES_CODES if k != "English (Latin)")

# Source codes that are Indic (not English)
INDIC_SOURCE_CODES = {v for k, v in FLORES_CODES.items() if k != "English (Latin)"}
