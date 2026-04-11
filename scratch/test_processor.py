import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import wave
import numpy as np
from audio.capture import AudioCaptureEngine
from audio.processor import AudioProcessor

def save_wav(filename, audio_data, sample_rate=16000):
    # Normalize
    if len(audio_data) > 0 and np.max(np.abs(audio_data)) > 0:
        audio_data = audio_data / np.max(np.abs(audio_data))
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

def run_vad_test():
    engine = AudioCaptureEngine(sample_rate=16000)
    processor = AudioProcessor(sample_rate=16000)
    
    print("\n[VAD PROCESSOR TEST]")
    print("Speak naturally. Play some YouTube music quietly in the background if you want.")
    print("Try speaking a complete sentence, then PAUSING for 1 second.\n")
    
    audio_generator = engine.capture_and_mix(mode="conference")
    
    # Run for exactly 15 seconds
    start_time = time.time()
    chunk_counter = 1
    
    try:
        # Pass the generator to the processor
        for processed_chunk, reason in processor.process_stream(audio_generator):
            duration = len(processed_chunk) / 16000
            print(f" -> SILENCE SLICE: Saved block {chunk_counter} ({duration:.2f} seconds)! Reason: {reason}")
            
            filename = f"scratch/test_processor_chunk_{chunk_counter}.wav"
            save_wav(filename, processed_chunk)
            chunk_counter += 1
            
            if time.time() - start_time > 15:
                print("15-second test complete! Shutting down...")
                break
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()

if __name__ == "__main__":
    run_vad_test()
