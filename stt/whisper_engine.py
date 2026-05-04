"""
PolyVerba - Whisper STT Engine (Faster-Whisper / CTranslate2)

Auto-detects CUDA GPU and selects the best model + precision automatically:
  GPU (CUDA): medium model, float16 — sub-0.5s transcription
  CPU:        base   model, int8   — ~0.5s transcription

Returns word-level data so the frontend can animate words one-by-one.
"""

import time
import numpy as np
import torch
from faster_whisper import WhisperModel


class WhisperEngine:
    def __init__(self, model_size_or_path="base", compute_type="int8", device="cpu"):
        # --- Auto-detect hardware ---
        if torch.cuda.is_available():
            device       = "cuda"
            compute_type = "float16"
            # If caller passed a CPU-default model, upgrade to medium for GPU
            if model_size_or_path in ("base", "base.en", "small", "tiny", "tiny.en"):
                model_size_or_path = "medium"
        else:
            device       = "cpu"
            compute_type = "int8"
            # If caller passed a GPU model, downgrade to base for CPU
            if model_size_or_path in ("medium", "large", "large-v2", "large-v3"):
                model_size_or_path = "base"

        # English-only models (.en suffix) cannot run task="translate"
        self.is_en_only = model_size_or_path.endswith(".en")
        self.sample_rate = 16000
        self.device = device

        print(f"[STT] Loading faster-whisper '{model_size_or_path}' model...")
        print(f"[STT] Device: {device.upper()} | Precision: {compute_type.upper()}")
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
        - beam_size=4:  beam search — sweet spot of accuracy vs speed
        - task_mode:    'transcribe' for .en models, 'translate' for multilingual
        - word_timestamps: get individual words for streaming animation
        """
        if len(audio_array) == 0:
            return "", []

        try:
            # .en models can only transcribe English natively
            # multilingual models use translate to always output English → IndicTrans2
            task_mode = "transcribe" if self.is_en_only else "translate"

            # Use beam=3 on CPU for a balance of speed and high accuracy, beam=4 on GPU
            beam = 4 if self.device == "cuda" else 3

            segments, info = self.model.transcribe(
                audio_array,
                beam_size=beam,
                language=language,
                task=task_mode,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
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
