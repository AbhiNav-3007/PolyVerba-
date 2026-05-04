"""
PolyVerba - System Audio Pipeline

Architecture: Two threads
  Thread 1 (Recorder)  — reads 0.1s micro-frames NON-STOP, never pauses
                         Captures at 44100Hz (native), resamples to 16kHz
  Thread 2 (Processor) — every 2s takes a 2.5s snapshot (0.5s overlap),
                         translates first, then streams words in TARGET language

Caption flow:  Translate → grey words (target language) → solid white line
Never shows English words when a translation target is selected.
"""

import threading
import queue
import time
import warnings
import re
import torch
import numpy as np
import collections

warnings.filterwarnings("ignore")

# ── Shared State ──────────────────────────────────────────────────────────────
result_queue    = queue.Queue()

_running        = False
_rec_thread     = None
_proc_thread    = None
_stt_engine     = None
_trans_engine   = None
_engines_loaded = False
_current_target = "English"   # default = English (no translation)
_capture_mode   = "loopback"
_on_gpu         = False       # set during engine load

_audio_queue    = queue.Queue(maxsize=2)   # Reduced from 8 to 2 to completely eliminate latency backlog

# ── Engine Loading ────────────────────────────────────────────────────────────

def _ensure_engines(model_size="base"):
    global _stt_engine, _trans_engine, _engines_loaded, _on_gpu

    from stt.whisper_engine import WhisperEngine
    from translation.indictrans_engine import IndicTransEngine

    # WhisperEngine auto-detects GPU internally and upgrades model to "medium" if CUDA
    print(f"\n[INIT] Loading Whisper (requested: '{model_size}')...")
    _stt_engine = WhisperEngine(model_size_or_path=model_size)
    _on_gpu = torch.cuda.is_available()
    print(f"[INIT] Hardware: {'GPU (CUDA)' if _on_gpu else 'CPU'}")

    if not _engines_loaded:
        print("[INIT] Loading IndicTrans2...")
        _trans_engine = IndicTransEngine()

    _engines_loaded = True
    print("[INIT] Engines ready!\n")


# ── Loopback Device ───────────────────────────────────────────────────────────

def _get_loopback_device():
    import soundcard as sc
    mics = sc.all_microphones(include_loopback=True)
    for m in mics:
        if "CABLE Output" in m.name and not m.isloopback:
            return m, f"VB-Cable ({m.name})"
    for m in mics:
        if m.isloopback and "CABLE" in m.name:
            return m, f"Loopback ({m.name})"
    for m in mics:
        if m.isloopback:
            return m, f"Loopback ({m.name})"
    return None, None


# ── Hallucination Filter ───────────────────────────────────────────────────────

_HALLUCINATION = re.compile(
    r"^(thanks for watching|thank you\.?|please subscribe|subtitles|"
    r"www\.|http|copyright|\[music\]|\[applause\]|\.\.\.+|_{3,})$",
    re.IGNORECASE
)

def _is_hallucination(text: str) -> bool:
    t = text.strip().lower()
    if len(t) < 3:
        return True
    if _HALLUCINATION.match(t):
        return True
    parts = t.split()
    if len(parts) >= 4 and len(set(parts)) == 1:
        return True
    punct_chars = sum(1 for c in t if c in '.-_•·…।')
    if len(t) > 3 and punct_chars / len(t) > 0.40:
        return True
    alpha_chars = sum(1 for c in t if c.isalpha())
    if alpha_chars < 2:
        return True
    return False


# ── Audio Resampling ────────────────────────────────────────────────────────────

def _resample(audio: np.ndarray, from_rate: int, to_rate: int) -> np.ndarray:
    """High-quality resample using scipy anti-aliasing filter."""
    if from_rate == to_rate:
        return audio
    try:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(from_rate, to_rate)
        return resample_poly(audio, to_rate // g, from_rate // g)
    except ImportError:
        # Fallback: naive decimation (less ideal but works)
        step = from_rate / to_rate
        indices = np.arange(0, len(audio), step).astype(int)
        indices = indices[indices < len(audio)]
        return audio[indices]


# ── Deduplication (overlap window) ───────────────────────────────────────────

def _deduplicate(current_words, prev_words, max_overlap=5):
    """Remove words from start of current that duplicate end of prev (overlap region)."""
    if not prev_words or not current_words:
        return current_words
    n = min(max_overlap, len(prev_words), len(current_words))
    for check in range(n, 0, -1):
        if prev_words[-check:] == current_words[:check]:
            return current_words[check:]
    return current_words


# ── Thread 1: Continuous Recorder ─────────────────────────────────────────────

def _recorder_thread(device, capture_rate, chunk_seconds, step_seconds):
    global _running
    MICRO   = 0.1
    micro_n = int(capture_rate * MICRO)
    maxlen  = int(capture_rate * (chunk_seconds + 1.0))
    buf     = collections.deque(maxlen=maxlen)
    last_push = time.time()

    TARGET_RATE = 16000

    try:
        with device.recorder(samplerate=capture_rate, channels=1) as rec:
            print(f"[AUDIO] Recorder started — capture={capture_rate}Hz → resample to {TARGET_RATE}Hz")
            print(f"[AUDIO] Window: {chunk_seconds}s | Step: {step_seconds}s | Overlap: {chunk_seconds-step_seconds:.1f}s")
            
            while _running:
                frame = rec.record(numframes=micro_n)
                buf.extend(frame[:, 0].astype(np.float32))

                now = time.time()
                if now - last_push >= step_seconds and len(buf) >= int(capture_rate * chunk_seconds):
                    snap_raw = np.array(list(buf)[-int(capture_rate * chunk_seconds):])
                    snap_16k = _resample(snap_raw, capture_rate, TARGET_RATE)
                    
                    try:
                        _audio_queue.put_nowait(snap_16k)
                    except queue.Full:
                        try: _audio_queue.get_nowait()
                        except: pass
                        try: _audio_queue.put_nowait(snap_16k)
                        except: pass
                    last_push = now
    except Exception as e:
        print(f"[RECORDER ERROR] {e}")
    finally:
        _running = False
        print("[AUDIO] Recorder stopped.")


# ── Thread 2: STT + Translation Processor ─────────────────────────────────────

def _processor_thread(source_lang):
    """
    Main pipeline loop.
    """
    global _running, _current_target
    from stt.translate import FLORES_CODES

    prev_words = []   # list of strings from previous chunk (for deduplication)

    while _running:
        # ── Wait for next audio snapshot ──────────────────────────────────
        try:
            audio = _audio_queue.get(timeout=1.5)
        except queue.Empty:
            continue

        if audio is None or not _running:
            break

        chunk_start = time.time()

        # ── 1. STT ────────────────────────────────────────────────────────
        try:
            lang_hint  = source_lang if source_lang not in ("auto", None, "en") else None
            full_text, word_strings = _stt_engine.transcribe_chunk(
                audio, language=lang_hint
            )
            # word_strings: list[str]  e.g. ["Hello,", "how", "are", "you?"]
        except Exception as e:
            print(f"[STT ERROR] {e}")
            continue

        if not full_text or not word_strings:
            continue

        if _is_hallucination(full_text.strip()):
            print(f"[FILTER] Hallucination dropped: {full_text.strip()!r}")
            continue

        # ── 2. Deduplication: strip overlap words from start ──────────────
        # Normalise for comparison only — keep original capitalisation for display
        norm_prev    = [w.strip().lower().strip(".,!?") for w in prev_words]
        norm_current = [w.strip().lower().strip(".,!?") for w in word_strings]
        skip = 0
        n = min(5, len(norm_prev), len(norm_current))
        for check in range(n, 0, -1):
            if norm_prev[-check:] == norm_current[:check]:
                skip = check
                break

        deduped_words = word_strings[skip:]   # original-case strings
        prev_words    = word_strings          # update for next chunk

        if not deduped_words:
            continue

        unique_text = " ".join(deduped_words).strip()
        if len(unique_text) < 3:
            continue

        # ── 3. Translate then stream in TARGET language ───────────────────
        try:
            current_tgt = _current_target   # read live (can change mid-stream)

            if current_tgt == "English":
                # No translation needed — stream English words as grey
                _stream_words(deduped_words, delay=0.09)
                result_queue.put({
                    "type":    "final",
                    "text":    unique_text,
                    "latency": round(time.time() - chunk_start, 2)
                })

            else:
                tgt_code = FLORES_CODES.get(current_tgt, "hin_Deva")
                src_code = FLORES_CODES.get("English", "eng_Latn")

                # Determine correct source FLORES code for non-English source
                if source_lang not in ("en", "auto", None):
                    from stt.translate import FLORES_TO_NAME, INDIC_SOURCE_CODES
                    _lang_map = {
                        "hi": "hin_Deva", "ta": "tam_Taml", "te": "tel_Telu",
                        "kn": "kan_Knda", "ml": "mal_Mlym", "mr": "mar_Deva",
                        "bn": "ben_Beng", "gu": "guj_Gujr", "pa": "pan_Guru",
                        "ur": "urd_Arab", "as": "asm_Beng", "ne": "npi_Deva",
                        "or": "ory_Orya",
                    }
                    src_code = _lang_map.get(source_lang, "eng_Latn")

                translated = _trans_engine.translate(
                    unique_text,
                    target_lang=tgt_code,
                    source_lang=src_code
                )

                if not translated or len(translated.strip()) < 2:
                    # Fallback: show English if translation fails
                    result_queue.put({
                        "type":    "final",
                        "text":    unique_text,
                        "latency": round(time.time() - chunk_start, 2)
                    })
                    continue

                # Stream translated words as grey, then push white final
                # Clean emergency "छे" word filter
                filtered = [w for w in translated.split() if not w.startswith("छे")]
                translated = " ".join(filtered).strip()
                if not translated:
                    continue

                _stream_words(translated.split(), delay=0.08)
                result_queue.put({
                    "type":    "final",
                    "text":    translated.strip(),
                    "latency": round(time.time() - chunk_start, 2)
                })

        except Exception as e:
            print(f"[PROCESS ERROR] {e}")
            import traceback; traceback.print_exc()
            continue   # skip this chunk, keep the thread alive
            
        # ── VRAM Anti-Fragmentation Cleanup ──────────────────────────────
        if _on_gpu:
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass

    print("[AUDIO] Processor stopped.")


def _stream_words(words, delay=0.06):
    """Push words rapidly for word-by-word fade-in animation."""
    for w in words:
        if not _running:
            break
        w = w.strip()
        if w:
            result_queue.put({"type": "word", "text": w})
            time.sleep(delay)


# ── Public API ─────────────────────────────────────────────────────────────────

def start_transcription(source_lang="en", target_lang="English",
                        model="base", translate=True, capture_mode="loopback"):
    global _running, _rec_thread, _proc_thread, _capture_mode, _current_target

    if _running:
        return False

    try:
        _ensure_engines(model)
        _capture_mode   = capture_mode
        _current_target = target_lang

        # Clear stale audio
        while not _audio_queue.empty():
            try: _audio_queue.get_nowait()
            except: pass

        _running = True

        import soundcard as sc
        if capture_mode == "loopback":
            device, label = _get_loopback_device()
            if device is None:
                result_queue.put({"type": "error", "text": "VB-Cable not found."})
                _running = False
                return False
        else:
            device = sc.default_microphone()
            label  = f"Mic ({device.name})"

        CAPTURE_RATE  = 44100
        CHUNK_SECONDS = 2.5
        STEP_SECONDS  = 2.0

        print(f"[AUDIO] Device: {label}")

        def _com_recorder():
            try:
                import pythoncom; pythoncom.CoInitialize()
            except ImportError:
                pass
            _recorder_thread(device, CAPTURE_RATE, CHUNK_SECONDS, STEP_SECONDS)
            try:
                import pythoncom; pythoncom.CoUninitialize()
            except ImportError:
                pass

        _rec_thread  = threading.Thread(target=_com_recorder,
                                        daemon=True, name="PolyVerba-Recorder")
        _proc_thread = threading.Thread(target=_processor_thread, args=(source_lang,),
                                        daemon=True, name="PolyVerba-Processor")
        _rec_thread.start()
        _proc_thread.start()
        return True

    except Exception as e:
        print(f"[ERROR] Start failed: {e}")
        import traceback; traceback.print_exc()
        _running = False
        return False


def stop_transcription():
    global _running
    _running = False
    try: _audio_queue.put_nowait(None)   # wake up processor
    except: pass


def update_target(lang_name):
    global _current_target
    _current_target = lang_name
    print(f"[TARGET] Switched to: {lang_name}")


def is_running():
    return _running and _rec_thread is not None and _rec_thread.is_alive()


def get_capture_mode():
    return _capture_mode
