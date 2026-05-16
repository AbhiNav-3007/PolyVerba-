# Current model : facebook/nllb-200-distilled-600M
# Alternative A  : ai4bharat/indictrans2-en-indic-dist-200M  (pip install indic-nlp-library)
#                  indic-nlp-library handles all 22 Indian scripts natively
# Alternative B  : ai4bharat/indictrans2-en-indic-1B          (highest accuracy, GPU recommended)
import os
import sys
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "models", "nllb-600m-ct2")

if os.path.exists(os.path.join(OUTPUT_DIR, "model.bin")):
    print(f"[SKIP] Model already converted at: {OUTPUT_DIR}")
    sys.exit(0)

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[INFO] Output directory: {OUTPUT_DIR}")
print("[INFO] Converting facebook/nllb-200-distilled-600M to CTranslate2 INT8 format...")

# Use ct2-transformers-converter
ct2_converter_path = os.path.join(os.path.dirname(sys.executable), "ct2-transformers-converter")
if sys.platform == "win32":
    ct2_converter_path += ".exe"

cmd = [
    ct2_converter_path,
    "--model", "facebook/nllb-200-distilled-600M",
    "--output_dir", OUTPUT_DIR,
    "--quantization", "int8",
    "--force"
]

print(f"[INFO] Running command: {' '.join(cmd)}")
result = subprocess.run(cmd)

if result.returncode == 0:
    print(f"\n[SUCCESS] Model converted and saved to: {OUTPUT_DIR}")
else:
    print("\n[ERROR] Conversion failed")
    sys.exit(1)
