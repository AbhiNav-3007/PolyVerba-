import numpy as np
import pyaudio
import soundcard as sc
import threading
import queue

class AudioCaptureEngine:
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.mic_q = queue.Queue(maxsize=50)
        self.loop_q = queue.Queue(maxsize=50)
        self.is_running = False

    def start_microphone_stream(self):
        try:
            default_mic = sc.default_microphone()
            with default_mic.recorder(samplerate=self.sample_rate, channels=1) as mic:
                while self.is_running:
                    data = mic.record(numframes=self.chunk_size)
                    audio_data = data[:, 0].astype(np.float32)
                    if self.mic_q.full(): self.mic_q.get_nowait()
                    self.mic_q.put(audio_data)
        except Exception as e:
            print(f"[Mic error] {e}")

    def start_loopback_stream(self):
        try:
            default_spk_name = sc.default_speaker().name
            mics = sc.all_microphones(include_loopback=True)
            # 1. Try to find the exact default speaker loopback
            loopback_mic = next((m for m in mics if m.isloopback and default_spk_name in m.name), None)
            
            # 2. Fallback to generic "Speaker" loopback
            if not loopback_mic:
                loopback_mic = next((m for m in mics if m.isloopback and "Speaker" in m.name), None)
                
            # 3. Absolute last resort fallback
            if not loopback_mic:
                loopback_mic = next((m for m in mics if m.isloopback), None)
                
        except Exception as e:
            print(f"[Loopback init error] {e}")
            return
            
        if not loopback_mic:
            print("[Warning] No OS Loopback device found.")
            return

        try:
            with loopback_mic.recorder(samplerate=self.sample_rate, channels=1) as mic:
                while self.is_running:
                    # NOTE: Windows Loopback blocks forever here if NO audio is playing! 
                    data = mic.record(numframes=self.chunk_size)
                    audio_data = data[:, 0].astype(np.float32)
                    if self.loop_q.full(): self.loop_q.get_nowait()
                    self.loop_q.put(audio_data)
        except Exception as e:
            print(f"[Loopback error] {e}")

    def capture_and_mix(self, mode="conference"):
        """
        mode: 
          - "conference": Captures both Microphone and Loopback equally (Zoom).
          - "broadcast": Captures ONLY Loopback, mutes microphone (YouTube/Sports).
          - "seminar": Captures ONLY Microphone, mutes loopback (Live Stage Speaker).
        """
        self.is_running = True
        
        # Only spin up the hardware threads we actually need!
        if mode in ["conference", "seminar"]:
            threading.Thread(target=self.start_microphone_stream, daemon=True).start()
        if mode in ["conference", "broadcast"]:
            threading.Thread(target=self.start_loopback_stream, daemon=True).start()

        while self.is_running:
            # 1. Microphone Check
            if mode in ["conference", "seminar"]:
                try:
                    mic_chunk = self.mic_q.get(timeout=2.0)
                except queue.Empty:
                    continue 
            else:
                mic_chunk = np.zeros(self.chunk_size, dtype=np.float32)

            # 2. Loopback Check
            if mode in ["conference", "broadcast"]:
                try:
                    # If we are in purely broadcast mode, loopback becomes the Master Clock. Wait 2 seconds.
                    # Otherwise, mic is master clock, so loopback only has 0.01s to sync up.
                    timeout_val = 2.0 if mode == "broadcast" else 0.01
                    loop_chunk = self.loop_q.get(timeout=timeout_val)
                except queue.Empty:
                    if mode == "broadcast": continue 
                    loop_chunk = np.zeros(self.chunk_size, dtype=np.float32)
            else:
                loop_chunk = np.zeros(self.chunk_size, dtype=np.float32)
                
            # 3. Exact Mode Routing
            if mode == "conference":
                mixed_audio = (mic_chunk + loop_chunk) / 2.0
            elif mode == "seminar":
                mixed_audio = mic_chunk
            else: # broadcast
                mixed_audio = loop_chunk
                
            yield mixed_audio

    def stop(self):
        self.is_running = False
