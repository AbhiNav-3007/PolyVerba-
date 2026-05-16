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
- **Translation:** `facebook/nllb-200-distilled-600M` — 600M parameter distilled model, CPU-optimized with CTranslate2
  > *Alternative: `ai4bharat/indictrans2-en-indic-dist-200M` (via `pip install indic-nlp-library` — handles all 22 Indian scripts natively) or `ai4bharat/indictrans2-en-indic-1B` for highest accuracy on GPU.*
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
Standard LLMs output ghost tokens at the start of every sentence. PolyVerba eliminates this permanently.

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

### 🔸 6. Universal Hardware Auto-Detection (CPU/GPU)
Seamlessly supports both standard laptops and high-performance NVIDIA hardware without separate code branches.

- Dynamically detects CUDA availability at runtime via `torch.cuda.is_available()`.
- Auto-scales precision: uses `float16` in VRAM for GPU (~0.3s latency) or falls back to `int8` in RAM for CPU (~1.5s latency).
- Ensures the exact same codebase runs flawlessly on a standard laptop or a dedicated heavy-compute workstation.
- **Tech Stack:** `PyTorch`, `CUDA`, `faster-whisper`

### 🔸 7. Cloud Compute Layer — GPU-Accelerated Translation
Deploy the full PolyVerba stack on AWS `g4dn.xlarge` (NVIDIA T4, 16GB VRAM) using the Meta NLLB-600M model for perfect native-script output across all languages.

- Edge vs Cloud latency comparison UI (`~1.5s CPU` vs `~0.4s GPU`)
- All 12 Indian scripts in correct native alphabet (Kannada, Tamil, Telugu, Gujarati native scripts)
- **Tech Stack:** `AWS EC2`, `CUDA`, `facebook/nllb-200-distilled-600M`
  > *Alternative: `ai4bharat/indictrans2-en-indic-1B` (via `indic-nlp-library`) for superior Indian language output on the same GPU.*

### 🔸 8. Dual-Mode RAG Glossary System
Prevent STT from misspelling domain-specific terminology (medical, legal, technical events).

- **Pre-Event Mode:** Organizer uploads PDF slides → local LLM extracts rare terms → injects into Whisper `hotwords`
- **Live Mode:** `spaCy` zero-shot NER scans live transcript → auto-caches new proper nouns mid-session
- **Tech Stack:** `Ollama LLM`, `spaCy`, `faster-whisper` hotwords API

### 🔸 9. Speaker Diarization
Automatically tag speaker identity during Q&A sessions without knowing who anyone is.

- `pyannote.audio` voiceprint clustering assigns `[Speaker 1]`, `[Speaker 2]` labels in real time
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
- **Translation:** `facebook/nllb-200-distilled-600M` — 600M parameter distilled model, CPU-optimized with CTranslate2
  > *Alternative: `ai4bharat/indictrans2-en-indic-dist-200M` (via `pip install indic-nlp-library` — handles all 22 Indian scripts natively) or `ai4bharat/indictrans2-en-indic-1B` for highest accuracy on GPU.*
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
Standard LLMs output ghost tokens at the start of every sentence. PolyVerba eliminates this permanently.

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

### 🔸 6. Universal Hardware Auto-Detection (CPU/GPU)
Seamlessly supports both standard laptops and high-performance NVIDIA hardware without separate code branches.

- Dynamically detects CUDA availability at runtime via `torch.cuda.is_available()`.
- Auto-scales precision: uses `float16` in VRAM for GPU (~0.3s latency) or falls back to `int8` in RAM for CPU (~1.5s latency).
- Ensures the exact same codebase runs flawlessly on a standard laptop or a dedicated heavy-compute workstation.
- **Tech Stack:** `PyTorch`, `CUDA`, `faster-whisper`

### 🔸 7. Cloud Compute Layer — GPU-Accelerated Translation
Deploy the full PolyVerba stack on AWS `g4dn.xlarge` (NVIDIA T4, 16GB VRAM) using the Meta NLLB-600M model for perfect native-script output across all languages.

- Edge vs Cloud latency comparison UI (`~1.5s CPU` vs `~0.4s GPU`)
- All 12 Indian scripts in correct native alphabet (Kannada, Tamil, Telugu, Gujarati native scripts)
- **Tech Stack:** `AWS EC2`, `CUDA`, `facebook/nllb-200-distilled-600M`
  > *Alternative: `ai4bharat/indictrans2-en-indic-1B` (via `indic-nlp-library`) for superior Indian language output on the same GPU.*

### 🔸 8. Dual-Mode RAG Glossary System
Prevent STT from misspelling domain-specific terminology (medical, legal, technical events).

- **Pre-Event Mode:** Organizer uploads PDF slides → local LLM extracts rare terms → injects into Whisper `hotwords`
- **Live Mode:** `spaCy` zero-shot NER scans live transcript → auto-caches new proper nouns mid-session
- **Tech Stack:** `Ollama LLM`, `spaCy`, `faster-whisper` hotwords API

### 🔸 9. Speaker Diarization
Automatically tag speaker identity during Q&A sessions without knowing who anyone is.

- `pyannote.audio` voiceprint clustering assigns `[Speaker 1]`, `[Speaker 2]` labels in real time
- **Tech Stack:** `pyannote.audio`

### 🔸 10. QR-Code Audience Interface
Each attendee's phone becomes a personalized caption screen — no app download required.

- Audiences scan QR displayed on main projector → browser opens captioning UI → select own language
- **Tech Stack:** `React`, `Vite`, `qrcode`

---

## 🔭 Future Scalability & Implementation Roadmap

> Everything below is designed with one constraint: **edge-first**. Every feature must be capable of running entirely on a local device — no internet, no cloud dependency, no subscription. Cloud is an optional upgrade, never a requirement.

---

### 🚀 F1 — Speaker Recognition & Diarization *(Edge)*
In a multi-speaker event — a panel, a debate, a parliamentary session — viewers currently receive captions without knowing *who* said what. This feature automatically identifies each speaker and prefixes their captions with a label like `[Speaker 1]` or `[Dr. Sharma]` if the speaker has been pre-registered. Runs entirely on the edge device — no audio leaves the room.

---

### 🚀 F2 — Intelligent Acoustic Focus & Noise Isolation *(Edge)*
Indian event venues are acoustically hostile — ceiling fans, open windows, crowd chatter, PA feedback, and reverb all degrade transcription accuracy. Instead of simple volume thresholds, this feature builds a continuous voice model of the target speaker from the first 10 seconds of speech, then uses that model as a lens — amplifying only the speaker's voice frequency signature and suppressing everything else in real time. The entire isolation runs on the edge device. No audio is ever uploaded.

---

### 🚀 F3 — Cloud Deployment & Hybrid Edge-Cloud Mode *(Optional Upgrade)*
For national-scale events — Parliament, national conferences, public broadcasts — where hundreds of simultaneous languages and thousands of concurrent viewers are required, PolyVerba can optionally be deployed to a cloud GPU server. The edge mode remains the default offline fallback. Cloud is an upgrade for capacity, not a dependency for functionality.

---

### 🚀 F4 — Train Our Own Noise Cancellation & Diarization Models *(Edge)*
Pretrained AI models for noise cancellation and speaker separation are trained on Western studio recordings and do not perform well in Indian acoustic environments. The plan is to collect real recordings from Indian venues — conference halls, classrooms, open-air stages, panchayat meeting spaces — label them, and train lightweight models tuned specifically for these conditions. The resulting models will be small enough to deploy on the same edge device, with no cloud inference.

---

### 🚀 F5 — Context-Aware Conversational AI *(Edge)*
The current pipeline processes each audio chunk independently with no memory of what came before. A context model would maintain a running understanding of the session — tracking which topic is being discussed, which proper nouns have appeared, and what the speaker's intent is — so that ambiguous or partially heard words are resolved using context rather than guesswork. "Arby I" becomes "RBI." "Modi" is never mis-transcribed. "crore" is never written as "crow". Runs locally on the edge device using a compact language model.

---

### 🚀 F6 — Colloquial & Natural Language Translation *(Edge)*
The current translation model outputs formal language because it was trained on formal sources — Wikipedia, news articles, religious texts. But live speech is informal. The goal is to fine-tune our own translation model on conversational sources — movie dialogue, casual speech transcripts, informal writing — so that translations sound like how people actually talk. *"आप क्या कर रहे हो?"* instead of *"आप किस प्रकार कार्य कर रहे हैं?"* The fine-tuned model runs on the same edge device, replacing the current model with zero pipeline changes.

---

### 🚀 F7 — QR-Based Instant Joining *(Edge, Zero Internet)*
Asking audience members to manually connect to a hotspot and type an IP address creates unnecessary friction. A QR code displayed on the projector screen — containing the local network address — lets any phone scan and connect instantly using just the phone's camera. The QR is generated and displayed on the edge device. No internet, no domain name, no app required. Just scan and read.

---

### 🚀 F8 — Universal Device Support & Installable Application *(Edge)*
PolyVerba should run on any device a presenter might realistically bring to an event — an old laptop, a mid-range GPU machine, or even a modern phone. The plan is to make the system automatically choose the right processing mode based on available hardware, and to package it as a single installable application that requires no technical setup — just install and run. Target size: under 500MB including all AI models.

---

### 🚀 F9 — RAG-Based Dynamic Vocabulary *(Edge)*
Before an event, the organiser uploads the speaker's PDF slides, agenda, or a custom glossary. A local AI reads these documents and automatically extracts domain-specific terms — medical terms for a health conference, legal terms for a court session, ISRO mission names for a science event — and feeds them to the speech recognition engine as hints. The result: rare proper nouns and technical terms are never mis-heard or mis-translated, even the first time they are spoken. Everything runs offline on the edge device.

---

### 🚀 F10 — Text-to-Speech & Speech-to-Speech *(Edge)*
Instead of reading captions on a screen, a viewer's phone can speak the translated text directly into their earphone. The caption becomes audio in their language — making PolyVerba a real-time personal spoken interpreter. The first version uses voices already installed on the phone. A later version uses a fine-tuned neural voice model that runs on the edge device and produces near-human Indic language speech.

---

### 🚀 F11 — PolyVerba Edge Earpiece *(Hardware Product, Fully Edge)*
The most ambitious form factor: a self-contained wireless earpiece that requires no phone, no laptop, and no internet. The wearer puts it on, and the earpiece listens, understands, translates, and speaks — entirely on its own embedded AI chip. A village elder attending a government meeting in Delhi hears every word in their own language through the earpiece, with no setup. Target cost: ₹2,000. Fully edge. Fully offline. Fully independent.

---

## 💡 Additional Real-Life Problem Features

*These features address real accessibility and usability gaps that exist in live multilingual communication today:*

---

### ➕ F12 — Indian Sign Language (ISL) Caption Mode *(Edge)*
An estimated 63 lakh people in India are deaf or hard of hearing. Current captioning systems ignore them entirely. This feature would generate Indian Sign Language avatar animations from the live transcript and display them alongside text captions — making events accessible to the deaf community without any additional hardware on their side.

---

### ➕ F13 — Live Session Summary *(Edge)*
After every 5 minutes of speaking, the system automatically generates a brief summary of what was discussed — in the viewer's chosen language. A viewer who joined late, or whose attention drifted, can read a concise recap without asking anyone. Runs on the edge device using a compact summarization model.

---

### ➕ F14 — Audience Question Bridge *(Edge)*
A viewer reading captions in Hindi can type a question in Hindi. The system translates it to the speaker's language (English) and displays it on the host's screen. The presenter answers in English. The answer is transcribed and translated back to Hindi for the viewer. A complete bilingual Q&A without any interpreter — end-to-end on the edge device.

---

### ➕ F15 — Emergency Broadcast Override *(Edge)*
If a specific phrase is detected in the live speech — "please evacuate," "emergency," "fire alarm" — the system immediately broadcasts a high-visibility full-screen alert to all connected devices in all active languages simultaneously. This turns PolyVerba into a safety system in public venues, not just a captioning tool. Runs locally, no internet required.

---

### ➕ F16 — Caption Confidence Indicator *(Edge)*
When the speech recognition is uncertain about a word — due to an unfamiliar accent, background noise, or a rare term — the caption displays that word in a slightly different shade, signalling to the viewer: *"this word may not be accurate."* Viewers know when to pay extra attention to the speaker rather than relying solely on the caption. Zero additional compute required.

---

### ➕ F17 — Multi-Room Support *(Edge)*
A single edge server supports multiple simultaneous event rooms in the same venue. Room A runs a Hindi session. Room B runs an English session. Room C runs Tamil. Each room has its own QR code, its own language options, and its own independent caption stream — all served from one laptop running in a corridor. No cloud, no dedicated hardware per room.

---

### ➕ F18 — Offline Session Transcript Export *(Edge)*
At the end of a session, any viewer can download the full transcript of everything said, in their chosen language, as a formatted PDF — directly from the browser. No account, no email, no server upload. The transcript file is assembled on the edge device and downloaded via a direct browser link. A participant in a legal proceeding, a student at a lecture, or a journalist at a press conference walks away with a complete record.

---

<div align="center">
  <i>Edge-first. Offline-capable. Designed for the 800 million Indians who live where the cloud does not reach.</i>
  <br><br>
  <b>Every feature above is planned to run without internet. Cloud is an upgrade — never a dependency.</b>
</div>
