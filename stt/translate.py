"""
PolyVerba — Language Code Mappings
Maps human-readable language names to FLORES-200 BCP-47 codes used by IndicTrans2.
"""

FLORES_CODES = {
    "Hindi":     "hin_Deva",
    "Marathi":   "mar_Deva",
    "Tamil":     "tam_Taml",
    "Telugu":    "tel_Telu",
    "Kannada":   "kan_Knda",
    "Bengali":   "ben_Beng",
    "Gujarati":  "guj_Gujr",
    "Malayalam":  "mal_Mlym",
    "Punjabi":   "pan_Guru",
    "Odia":      "ory_Orya",
    "Urdu":      "urd_Arab",
    "Assamese":  "asm_Beng",
}

# Ordered list for the frontend dropdown
LANGUAGE_NAMES = ["English"] + sorted(FLORES_CODES.keys())
