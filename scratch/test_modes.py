import sys
import os
import wave
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio.capture import AudioCaptureEngine

def save_wav(frames, filename):
    if not frames:
        print(f"❌ Error: No frames captured for {filename}")
        return
        
    audio_data = np.concatenate(frames)
    max_amp = np.max(np.abs(audio_data))
    if max_amp > 0:
        audio_data = np.int16(audio_data / max_amp * 32767)
    else:
        audio_data = np.int16(audio_data)

    filepath = os.path.join(os.path.dirname(__file__), filename)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data.tobytes())
    print(f"✅ Saved: {filename}")

def run_mode_test(mode_name, duration=5):
    print(f"\n" + "="*50)
    print(f"STARTING {duration}-SECOND TEST: Mode = '{mode_name.upper()}'")
    print("="*50)
    
    engine = AudioCaptureEngine()
    frames = []
    
    start = time.time()
    for chunk in engine.capture_and_mix(mode=mode_name):
        frames.append(chunk)
        if time.time() - start > duration:
            break
            
    engine.stop()
    save_wav(frames, f"test_{mode_name}.wav")
    time.sleep(1) # Give hardware a second to cleanly close before next test

if __name__ == "__main__":
    print("\n--- POLYVERBA TRI-MODE AUDIO ENGINE VALIDATION ---")
    print("ACTION REQUIRED: Turn on YouTube music AND be ready to speak into the mic.")
    print("Ensure VB-Cable 'Listen to this device' logic is active!")
    print("Starting in 3 seconds...\n")
    time.sleep(3)
    
    # 1. Conference Mode (Both)
    print(">>> First Test: Conference (Expect Voice + YouTube)")
    run_mode_test("conference", duration=10)
    
    # 2. Broadcast Mode (Loopback only)
    print(">>> Second Test: Broadcast (Expect YouTube ONLY, no voice)")
    run_mode_test("broadcast", duration=10)
    
    # 3. Seminar Mode (Mic only)
    print(">>> Third Test: Seminar (Expect Voice ONLY, no YouTube)")
    run_mode_test("seminar", duration=10)
    
    print("\n🎉 ALL TESTS COMPLETE! Please review the 3 .wav files in the scratch directory.")
