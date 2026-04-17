import time
import sys
import os
import warnings

# Suppress the ugly Windows MediaFoundation audio dropout warnings 
warnings.filterwarnings("ignore", module="soundcard")

# Add the project root directory to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.capture import AudioCaptureEngine
from audio.processor import AudioProcessor
from stt.whisper_engine import WhisperEngine
from translation.indictrans_engine import IndicTransEngine

print("="*60)
print("🎙️ POLYVERBA: ULTIMATE FUSION (VAD + STT + PATH B STREAMING)")
print("="*60)

try:
    print("[1/3] Loading STT Engine (Whisper)...")
    stt_engine = WhisperEngine(model_size_or_path="small", compute_type="int8", device="cpu")
    
    print("[2/3] Loading Translation Engine (Path B - 200M)...")
    translation_engine = IndicTransEngine()
    
    print("[3/3] Spinning up Audio Engines (With Anti-Glitch Buffers)...")
    capture_engine = AudioCaptureEngine(sample_rate=16000, chunk_size=4096)
    processor = AudioProcessor(sample_rate=16000)
    
except Exception as e:
    print(f"Failed to load Engines: {e}")
    exit(1)

print("\n🚀 Setup Complete!")
print("Select your Presentation Mode:")
print("1. Seminar (Microphone only, ignores computer sounds)")
print("2. Broadcast (Computer sounds only, ignores microphone)")
print("3. Conference (Mixes both Microphone + Computer sounds)")

mode_choice = input("\nEnter Mode (1, 2, or 3): ").strip()
mode_map = {"1": "seminar", "2": "broadcast", "3": "conference"}
selected_mode = mode_map.get(mode_choice, "seminar")

print(f"\n🎧 Started listening in {selected_mode.upper()} mode. Speak naturally into your mic.")
print("The AI will slice your audio, Transcribe to English, and Stream to Hindi dynamically!")
print("Press Ctrl+C to stop.\n")

try:
    audio_generator = capture_engine.capture_and_mix(mode=selected_mode)

    for processed_chunk, slice_reason in processor.process_stream(audio_generator):
        
        chunk_duration = len(processed_chunk) / 16000.0
        print(f"\n[✂️ VAD CUT] Reason: {slice_reason} | Duration: {chunk_duration:.2f}s")
        
        # 1. Faster-Whisper Transcription
        start_stt = time.time()
        english_text = stt_engine.transcribe_chunk(processed_chunk, language="en")
        
        if not english_text.strip():
            continue
            
        print(f"🇬🇧  ENGLISH  : {english_text}")
        print(f"     (STT Time : {time.time() - start_stt:.2f}s)")
        
        # 2. Path B Translation Streaming
        print(f"🇮🇳  HINDI    : ", end="", flush=True)
        start_trans = time.time()
        first_token = None
        
        for hindi_chunk in translation_engine.translate_stream(english_text, target_lang="hin_Deva", source_lang="eng_Latn"):
            if first_token is None:
                first_token = time.time() - start_trans
            print(hindi_chunk, end="", flush=True)
            
        print(f"\n     (TTFT : {first_token:.2f}s | Translate Time: {time.time() - start_trans:.2f}s)")

except KeyboardInterrupt:
    print("\n🛑 Shutting down stream gracefully...")
    capture_engine.stop()
    print("Done.")
