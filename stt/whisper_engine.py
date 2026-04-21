"""
PolyVerba - Whisper STT Engine (Faster-Whisper / CTranslate2)

Returns word-level data so the frontend can animate words one-by-one.
"""

import time
import numpy as np
from faster_whisper import WhisperModel


class WhisperEngine:
    def __init__(self, model_size_or_path="small", compute_type="int8", device="cpu"):
        print(f"[STT] Loading faster-whisper '{model_size_or_path}' model...")
        print(f"[STT] Device: {device.upper()} | Precision: {compute_type.upper()}")

        self.sample_rate = 16000
        start_time = time.time()

        self.model = WhisperModel(
            model_size_or_path,
            device=device,
            compute_type=compute_type
        )
        print(f"[STT] Model loaded in {time.time() - start_time:.1f}s")

    def transcribe_chunk(self, audio_array: np.ndarray, language=None):
        """
        Transcribes audio. Returns (full_text, words_list).
        words_list is a list of word strings for word-by-word animation.

        - vad_filter:   built-in Silero VAD, eliminates silence hallucinations
        - beam_size=5:  top-5 beam search for 90%+ accuracy
        - word_timestamps: get individual words for streaming animation
        """
        if len(audio_array) == 0:
            return "", []

        try:
            segments, info = self.model.transcribe(
                audio_array,
                beam_size=5,
                language=language,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=300,
                    speech_pad_ms=200,
                ),
                word_timestamps=True,
                condition_on_previous_text=False,
            )

            full_text = ""
            words = []

            for segment in segments:
                # Skip segments that are likely silence/noise
                if segment.no_speech_prob >= 0.5:
                    continue
                for word in segment.words:
                    w = word.word.strip()
                    if w:
                        words.append(w)
                        full_text += word.word

            return full_text.strip(), words

        except Exception as e:
            print(f"[STT ERROR] {e}")
            return "", []
