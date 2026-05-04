"""
PolyVerba — Language Code Mappings

Maps human-readable language names to FLORES-200 codes used by IndicTrans2.
Also provides reverse mapping (FLORES → display name) for the 3-direction engine.

Correct FLORES codes verified against AI4Bharat's official tokenizer vocabulary.
"""

# Display name → FLORES-200 code (for translate() calls)
FLORES_CODES = {
    "Hindi":      "hin_Deva",
    "Marathi":    "mar_Deva",
    "Tamil":      "tam_Taml",   # Correct: tam_Taml not tam_Drav
    "Telugu":     "tel_Telu",
    "Kannada":    "kan_Knda",
    "Bengali":    "ben_Beng",
    "Gujarati":   "guj_Gujr",
    "Malayalam":  "mal_Mlym",
    "Punjabi":    "pan_Guru",
    "Odia":       "ory_Orya",
    "Urdu":       "urd_Arab",
    "Assamese":   "asm_Beng",
    "Nepali":     "npi_Deva",
    "English":    "eng_Latn",   # Used for indic-en direction
}

# FLORES code → display name (reverse lookup)
FLORES_TO_NAME = {v: k for k, v in FLORES_CODES.items()}

# Ordered list for the frontend dropdown (English first, rest alphabetical)
LANGUAGE_NAMES = ["English"] + sorted(k for k in FLORES_CODES if k != "English")

# Languages that need the indic-en model (source is Indic, target is English)
# and indic-indic model (both source and target are Indic)
INDIC_SOURCE_CODES = {v for k, v in FLORES_CODES.items() if k != "English"}
