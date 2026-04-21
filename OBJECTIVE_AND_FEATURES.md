<div align="center">

# 🌐 PolyVerba
**The Real-Time multilingual Speech-to-text translation matrix bridging zero-downtime Edge AI and Cloud APIs.**

[![Architecture](https://img.shields.io/badge/Architecture-Edge_AI_First-6D28D9?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/Languages-12_Indian_Scripts-7C3AED?style=for-the-badge)](#)
[![Offline](https://img.shields.io/badge/Edge_Mode-100%25_Offline-059669?style=for-the-badge)](#)
[![Latency](https://img.shields.io/badge/Edge_Latency-~1.5s_CPU-F59E0B?style=for-the-badge)](#)

<p align="center">
  <i>Engineered for zero downtime, zero hallucinations, and real-world live event deployment — on hardware you already own.</i>
</p>

</div>

---

## 🎯 Executive Objective

> **To eliminate the language barrier at live events, webinars, and broadcasts by delivering real-time speech translation into 12 Indian languages — operating with guaranteed continuity on offline Edge AI and scaling seamlessly to high-throughput Cloud compute when available.**

Live events in India fail non-native audiences daily. A Tamil delegate at an English-medium conference misses 80% of the content. A Hindi-speaking student watching a Kannada lecture has no recourse. Commercial real-time captioning tools are either English-only, cloud-dependent, or absurdly expensive for academic and civic events.

PolyVerba attacks this problem at three layers simultaneously:

1. **Reliability** — The system must function even when the venue internet fails. A fully-quantized Edge AI pipeline runs locally on a standard CPU laptop, requiring zero cloud connectivity at runtime.
2. **Accuracy** — Speech-to-text must handle Indian accents, code-mixing, and fast speakers. Translation must produce grammatically correct, script-accurate output in 12 languages without hallucinations.
3. **Accessibility** — The interface must be zero-friction: one click to start, live output in the browser, language switching without restarting the session.

---

## 💎 Core Architecture & Capabilities

### 🔷 1. Edge-First AI Pipeline *(Implemented)*
The foundational compute layer runs entirely on the presenter's laptop with no internet dependency at runtime.

- **Speech-to-Text:** `faster-whisper` (CTranslate2 INT8 quantized) with Silero VAD for silence suppression
- **Translation:** `ai4bharat/indictrans2-en-indic-dist-200M` — 200M parameter distilled model, CPU-optimized
- **Continuous Audio:** Dual-threaded pipeline — non-stop recorder + async processor with 0.5s sliding overlap
- **Deduplication:** Sliding-window suffix-prefix matching eliminates repeated words from overlapping chunks
- **Tech Stack:** `faster-whisper`, `CTranslate2`, `transformers`, `torch`, `soundcard`, `numpy`, `threading`

### 🔷 2. StreamSync Audio Mode — Live Stream Translation *(Implemented)*
Captures internal system audio (not microphone) to translate any online audio source — Zoom calls, YouTube live streams, news broadcasts, sports commentary, online lectures — without any hardware changes.

- Intercepts OS-level loopback via `VB-Cable` virtual audio device
- Auto-detects `CABLE Output` device from Windows audio stack
- Zero microphone bleed — clean digital source guarantees higher STT accuracy
- Works with any application producing desktop audio
- **Tech Stack:** `soundcard` loopback API, `VB-Audio Virtual Cable`

### 🔷 3. Zero-Hallucination Translation *(Implemented)*
Standard IndicTrans2 outputs ghost tokens at the start of every sentence. PolyVerba eliminates this permanently.

- **BOS Token Excision:** Forces removal of the language-tag token from generated sequence (`[:, 1:]` tensor slice before decode)
- **Punctuation Artifact Filter:** Regex-based secondary cleanup of short leading tokens
- **Silence Artifact Filter:** Rejects outputs with >40% punctuation ratio, repeated-word spam, sub-3-char outputs
- **VAD Pre-filter:** Whisper's Silero VAD skips non-speech frames before STT even runs
- **Tech Stack:** `transformers`, `regex`, `faster-whisper` VAD

### 🔷 4. Continuous Flow Caption UI *(Implemented)*
A single, append-only paragraph replaces the traditional line-per-chunk subtitle approach.

- All output flows inline — natural CSS word-wrap at container boundary, absolutely no hyphens mid-word
- **Progressive Dimming:** 5-tier age-based dimming (95% → 70% → 45% → 28% → 15% opacity) shows recency at a glance
- **Grey Draft Animation:** Current draft words appear as purple-grey italic inline, replaced by bright white on confirmation — CSS `word-fade-in` animation, zero JS timing delays
- **Language Switch Label:** Centered uppercase label + decorative rule injected inline when user changes target language
- **Indic Script Fonts:** Full Noto Sans stack covering all 12 script families, with Windows system font fallbacks
- **Tech Stack:** Vanilla JS, Vanilla CSS, Google Fonts (Inter + Noto Sans Indic)

### 🔷 5. FastAPI WebSocket Real-Time Delivery *(Implemented)*
- Persistent WebSocket connections push caption events to all connected clients simultaneously
- Three event types: `{type:"word"}` (grey draft), `{type:"final"}` (white confirmed), `{type:"error"}`
- REST control layer: `POST /api/start`, `POST /api/stop`, `POST /api/update-target`
- Auto port-kill on startup prevents `[Errno 10048]` socket conflicts
- **Tech Stack:** `FastAPI`, `uvicorn`, `asyncio`, `starlette WebSockets`

---

### 🔸 6. Cloud Compute Layer — GPU-Accelerated Translation
Deploy the full PolyVerba stack on AWS `g4dn.xlarge` (NVIDIA T4, 16GB VRAM) using the `indictrans2-en-indic-1B` model for perfect native-script output across all 12 languages.

- Edge vs Cloud latency comparison UI (`~1.5s CPU` vs `~0.4s GPU`)
- All 12 Indian scripts in correct native alphabet (Kannada, Tamil, Telugu, Gujarati native scripts)
- **Tech Stack:** `AWS EC2`, `CUDA`, `indictrans2-en-indic-1B`

### 🔸 7. Dual-Mode RAG Glossary System
Prevent STT from misspelling domain-specific terminology (medical, legal, technical events).

- **Pre-Event Mode:** Organizer uploads PDF slides → local LLM extracts rare terms → injects into Whisper `hotwords`
- **Live Mode:** `spaCy` zero-shot NER scans live transcript → auto-caches new proper nouns mid-session
- **Tech Stack:** `Ollama LLM`, `spaCy`, `faster-whisper` hotwords API

### 🔸 8. Speaker Diarization
Automatically tag speaker identity during Q&A sessions without knowing who anyone is.

- `pyannote.audio` voiceprint clustering assigns `[Speaker 1]`, `[Speaker 2]` labels in real time
- **Tech Stack:** `pyannote.audio`

### 🔸 9. QR-Code Audience Interface
Each attendee's phone becomes a personalized caption screen — no app download required.

- Audiences scan QR displayed on main projector → browser opens captioning UI → select own language
- **Tech Stack:** `React`, `Vite`, `qrcode`

### 🔸 10. 4-Mode Compute Matrix table (2 dropdowns × 2 models)


---

<div align="center">
  <i>Edge system is production-ready. Cloud and advanced features in active development.</i>
</div>
