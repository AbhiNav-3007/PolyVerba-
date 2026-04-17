import numpy as np

class AudioProcessor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        
        # Option C Architecture: VAD-Adaptive Slicing Parameters
        self.energy_threshold = 0.0005      # Calibrated for Earbuds: pure silence is < 0.0002, speech is > 0.002
        self.breath_pause_sec = 0.4         # 400ms pause triggers an instant sentence-cut
        self.safety_timeout_sec = 2.0       # Maximum 2.0 seconds before forcing a chunk (latency barrier)
        self.overlap_sec = 0.5              # 500ms overlap to prevent chopping words in half

        # Internal conversion to frame counts
        self.breath_pause_frames = int(self.breath_pause_sec * self.sample_rate)
        self.safety_timeout_frames = int(self.safety_timeout_sec * self.sample_rate)
        self.overlap_frames = int(self.overlap_sec * self.sample_rate)

        # State Tracking
        self.audio_buffer = np.array([], dtype=np.float32)
        self.silence_frame_count = 0
        self.is_speaking = False

    def get_rms_energy(self, chunk):
        """Calculate Root Mean Square energy of the audio chunk."""
        if len(chunk) == 0:
            return 0.0
        return np.sqrt(np.mean(chunk**2))

    def process_stream(self, chunk_generator):
        """
        Consumes an infinite generator of audio chunks from capture.py.
        Yields perfectly sized, overlapping audio blocks based on VAD pauses.
        """
        for incoming_chunk in chunk_generator:
            # 1. Append new audio to our sliding window
            self.audio_buffer = np.concatenate((self.audio_buffer, incoming_chunk))
            
            # 2. Advanced Voice Activity Detection (VAD) via RMS Energy
            energy = self.get_rms_energy(incoming_chunk)
            
            if energy > self.energy_threshold:
                self.is_speaking = True
                self.silence_frame_count = 0  # Reset silence counter
            else:
                if self.is_speaking:
                    self.silence_frame_count += len(incoming_chunk)

            # 3. Determine if we must slice the buffer
            triggered = False
            reason = ""
            
            current_buffer_frames = len(self.audio_buffer)

            if self.is_speaking and self.silence_frame_count >= self.breath_pause_frames:
                triggered = True
                reason = "Natural Breath Pause"
                
            elif current_buffer_frames >= self.safety_timeout_frames:
                triggered = True
                reason = "Safety Timeout (2.0s exceeded)"

            # 4. Slicing and Overlap Logic
            if triggered:
                
                # [ANTI-HALLUCINATION FILTER] 
                # If we waited 2 seconds and nobody ever spoke, silently drop the buffer 
                # so we don't send pure silence to Whisper (which causes the 'Thank you' bug).
                if not self.is_speaking and "Safety Timeout" in reason:
                    self.audio_buffer = np.array([], dtype=np.float32)
                    continue
                    
                # Yield the entire active buffer to the AI Translator
                chunk_to_translate = self.audio_buffer.copy()
                yield (chunk_to_translate, reason)
                
                # Overlap: Keep the last 0.5 seconds to preserve context for the next slice
                if len(self.audio_buffer) > self.overlap_frames:
                    self.audio_buffer = self.audio_buffer[-self.overlap_frames:]
                
                # Reset State for next slice
                self.is_speaking = False
                self.silence_frame_count = 0
