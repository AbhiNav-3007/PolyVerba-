import os
import time
import numpy as np
from faster_whisper import WhisperModel

class WhisperEngine:
    def __init__(self, model_size_or_path="large-v3", compute_type="int8", device="cpu"):
        """
        Initializes the STT Engine using Faster-Whisper.
        
        Using INT8 on the CPU aggressively shrinks the model's memory footprint
        down to ~1.5GB to safely run on 8GB laptops without crashing Windows.
        """
        print(f"[STT INIT] Loading {model_size_or_path} model...")
        print(f"[STT INIT] Hardware target: {device.upper()} running natively in {compute_type.upper()} precision.")
        
        self.sample_rate = 16000
        start_time = time.time()
        
        try:
            # We enforce CPU INT8 to prevent your 8GB Ryzen laptop from Out-of-Memory crashing.
            self.model = WhisperModel(
                model_size_or_path, 
                device=device,
                compute_type=compute_type
            )
            print(f"[STT INIT] Model loaded successfully in {time.time() - start_time:.2f} seconds!")
        except Exception as e:
            print(f"[STT ERROR] Failed to load model: {e}")
            raise e

    def transcribe_chunk(self, audio_array: np.ndarray, language=None) -> str:
        """
        Takes a raw numpy float32 array (sliced directly from our AudioProcessor VAD)
        and transcribes it instantly without writing to the hard drive.
        """
        if len(audio_array) == 0:
            return ""

        try:
            # We disable condition_on_previous_text. Live events are unpredictable.
            # We want zero-shot transcription for absolute latency speed.
            segments, info = self.model.transcribe(
                audio_array,
                beam_size=1, # Lowest beam size = absolute fastest latency
                language=language,
                condition_on_previous_text=False
            )
            
            transcription = "".join([segment.text for segment in segments])
            return transcription.strip()
            
        except Exception as e:
            print(f"[STT TRANSCRIPTION ERROR] {e}")
            return ""
