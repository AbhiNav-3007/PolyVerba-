import sys
import os
import wave
import time
import numpy as np
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio.capture import AudioCaptureEngine

def run_loopback_test():
    engine = AudioCaptureEngine()
    engine.is_running = True
    
    # Start ONLY the loopback stream
    threading.Thread(target=engine.start_loopback_stream, daemon=True).start()
    
    print("\n" + "="*50)
    print("STARTING 10-SECOND LOOPBACK ONLY TEST")
    print("="*50)
    print("ACTION REQUIRED: PLAY a Youtube video with MULTIMEDIA AUDIO right now!")
    print("If wearing headphones, play it through the headphones.")
    print("...")

    frames = []
    start = time.time()
    
    while engine.is_running:
        try:
            # We must access the new loop_q directly for this isolated test
            chunk = engine.loop_q.get(timeout=0.1)
            frames.append(chunk)
        except:
            pass
            
        if time.time() - start > 10:
            break
            
    engine.stop()

    if len(frames) == 0:
        print("❌ Error: No loopback frames were captured.")
        return

    # Save to wave file
    audio_data = np.concatenate(frames)
    max_amp = np.max(np.abs(audio_data))
    
    if max_amp > 0:
        audio_data = np.int16(audio_data / max_amp * 32767)
    else:
        audio_data = np.int16(audio_data)

    filepath = os.path.join(os.path.dirname(__file__), "loopback_only.wav")
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data.tobytes())

    print(f"\n✅ TEST COMPLETE! Loopback audio saved to: {filepath}")
    print("Open it. You should ONLY hear YouTube, zero background microphone noise.\n")

if __name__ == "__main__":
    run_loopback_test()
