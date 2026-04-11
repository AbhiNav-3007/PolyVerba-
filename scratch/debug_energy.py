import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import soundcard as sc
import time

SAMPLE_RATE = 16000
CHUNK_SIZE  = 1024

print("[MIC ENERGY CALIBRATOR]")
print("Speak normally for 8 seconds. Watch the energy values.\n")

mic = sc.default_microphone()
readings = []

with mic.recorder(samplerate=SAMPLE_RATE, channels=1) as recorder:
    start = time.time()
    while time.time() - start < 8:
        data = recorder.record(numframes=CHUNK_SIZE)
        chunk = data[:, 0].astype(np.float32)
        rms = float(np.sqrt(np.mean(chunk**2)))
        readings.append(rms)
        print(f"  RMS Energy: {rms:.6f}")

print("\n--- CALIBRATION SUMMARY ---")
print(f"  Minimum (pure silence) : {min(readings):.6f}")
print(f"  Maximum (loudest voice) : {max(readings):.6f}")
print(f"  Average (all readings)  : {np.mean(readings):.6f}")
recommended = np.mean(readings[:5]) * 3  # 3x silence average
print(f"\n  RECOMMENDED threshold   : {recommended:.6f}")
print("\nPaste that recommended threshold into audio/processor.py as energy_threshold!")
