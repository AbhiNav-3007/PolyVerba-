<div align="center">

# PolyVerba
## Real-Time Multilingual Captioning — Edge AI, Zero Internet

---

> *"One speaker. Any language. Every device. No internet."*

---

[![Offline First](https://img.shields.io/badge/🔒_Offline_First-100%25_Edge_AI-059669?style=for-the-badge)](#)
[![Languages](https://img.shields.io/badge/🌏_Languages-22+_Indian_Scripts-7C3AED?style=for-the-badge)](#)
[![Latency](https://img.shields.io/badge/⚡_Latency-~0.9s_CPU-F59E0B?style=for-the-badge)](#)
[![Devices](https://img.shields.io/badge/📱_Multicast-500+_Devices-3B82F6?style=for-the-badge)](#)

</div>

---

## 🔴 The Problem

**India has 22 official languages. Most live events have only one.**

Every day, in conferences, colleges, Parliament sessions, and civic meetings across India — millions of people sit in silence because the speaker isn't using their language. Commercial tools are either:

- 🚫 **English-only** (Google Live Transcribe, Otter.ai)
- 🚫 **Cloud-dependent** (fail the moment Wi-Fi drops)
- 🚫 **Expensive** (enterprise licenses beyond academic reach)

> **There is no offline, real-time, multi-language captioning solution for Indian languages. PolyVerba is that solution.**

---

## ✅ The Solution — PolyVerba in One Line

**A laptop runs a local AI server. Hundreds of phones connect over Wi-Fi. Each person reads captions in their own language. No internet. No app download. No cost.**

---

## 🧠 What Makes It Different

| Feature | PolyVerba | Competitors |
|---------|-----------|-------------|
| Works without internet | ✅ Yes | ❌ No |
| Multiple languages simultaneously | ✅ Up to 4 live | ❌ 1 at a time |
| Phones connect without app install | ✅ Browser URL only | ❌ App required |
| Runs on a standard laptop CPU | ✅ Yes | ❌ Cloud GPU required |
| Indian scripts (Devanagari, Tamil, etc.) | ✅ 22+ languages | ⚠️ Limited |
| Per-device language selection | ✅ Yes, independent | ❌ No |
| Latency | ✅ ~0.9 seconds | ⚠️ 1.5–3s |

---

## ⚙️ The Architecture — How It Works

```
┌────────────────────────── YOUR LAPTOP ────────────────────────────┐
│                                                                    │
│  🎤 Audio Input          🤖 Faster-Whisper       🔁 Meta NLLB-600M │
│  (Mic or VB-Cable)  ──▶  Speech-to-Text     ──▶  Translate to     │
│  Captured at 44.1kHz     CTranslate2 INT8        22+ Languages    │
│  Resampled to 16kHz      Silero VAD filter       CPU optimized    │
│  2s chunks / 1.3s step   ~0.6s latency           ~0.3s/language   │
│                                    │                               │
│              FastAPI Web Server (http://192.168.137.1:8080)        │
│              Tracks which phone wants which language               │
└────────────────────────────────────┬──────────────────────────────┘
                                     │  Wi-Fi  (LAN / Mobile Hotspot)
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
        ┌─────▼──────┐        ┌──────▼─────┐        ┌──────▼─────┐
        │ 📱 Judge 1  │        │ 📱 Judge 2  │        │ 📱 Judge 3  │
        │   Hindi     │        │   Tamil     │        │   Telugu   │
        │ नमस्ते दोस्तों │        │ வணக்கம்...  │        │ నమస్కారం...│
        └────────────┘        └────────────┘        └────────────┘
             Browser — no app, just a URL. Zero internet needed.
```

---

## 🔑 Core Pillars

### Pillar 1 — 🔒 100% Offline Edge AI
All AI models run locally. Once downloaded, **the system never contacts the internet again.**
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` set at startup — zero cloud call risk.
- Models cached locally in the `/models` directory.
- Works in remote venues, conference halls, and anywhere with zero Wi-Fi.

### Pillar 2 — ⚡ Sub-1-Second Latency Pipeline
Two parallel background threads ensure the AI never blocks the audio recorder.

| Stage | Technology | Time |
|-------|-----------|------|
| Audio capture & resample | SoundCard + SciPy | Always running |
| Voice Activity Detection | Silero VAD (in Whisper) | ~0ms (pre-filter) |
| Speech-to-Text | Faster-Whisper INT8 | ~0.6s |
| Translation (per language) | Meta NLLB-600M INT8 | ~0.3s |
| WebSocket delivery to phones | FastAPI + asyncio | ~5ms |
| **Total end-to-end** | | **~0.9s** |

### Pillar 3 — 📡 Dynamic Subscription Multicast
Each phone independently tells the server which language it wants.

```
Phone A connects → subscribes to "Hindi"
Phone B connects → subscribes to "Tamil"
Phone C connects → subscribes to "Telugu"

Server translates English → Hindi, Tamil, Telugu (3 NLLB passes)
Server sends ONLY Hindi to Phone A
Server sends ONLY Tamil to Phone B
Server sends ONLY Telugu to Phone C

500 phones connected? CPU still does ONLY 3 translation passes.
Load is FLAT regardless of number of viewers.
```

> **This is Server-Side Multicasting. The CPU scales with unique languages, not devices.**

### Pillar 4 — 🛡️ Zero-Hallucination Filter Stack
Whisper generates "ghost" tokens during silence. PolyVerba eliminates them:

1. **Silero VAD** — Discards non-speech frames before Whisper runs
2. **Min-length check** — Rejects outputs under 3 characters
3. **Blacklist regex** — Blocks "thanks for watching", "subscribe", "[music]", URLs, etc.
4. **Repetition detector** — Blocks outputs like "the the the the"
5. **Punctuation ratio** — Rejects outputs with >40% punctuation characters
6. **Deduplication** — Sliding-window removes overlap words between 2s audio chunks

### Pillar 5 — 🎨 Premium Zero-Friction UI
- **No app install** — judges open a browser URL, that's it.
- **Glassmorphism dark UI** — premium purple theme, Noto Sans Indic fonts for all 22 scripts.
- **Continuous flow paragraph** — captions flow naturally, newest text bright, oldest text fades out.
- **Live latency badge** — shows AI processing time in real time (e.g. `⊙ 0.9s`).
- **Host / Viewer separation** — Start/Stop only visible on your laptop. Phones see only captions + language selector.

---

## 🌍 Supported Languages (All 22 Official + English)

| # | Language | Script | # | Language | Script |
|---|----------|--------|---|----------|--------|
| 1 | Hindi | Devanagari | 12 | Odia | Odia |
| 2 | Tamil | Tamil | 13 | Nepali | Devanagari |
| 3 | Telugu | Telugu | 14 | Sindhi | Arabic |
| 4 | Kannada | Kannada | 15 | Bodo | Devanagari |
| 5 | Malayalam | Malayalam | 16 | Dogri | Devanagari |
| 6 | Marathi | Devanagari | 17 | Kashmiri | Arabic |
| 7 | Bengali | Bengali | 18 | Konkani | Devanagari |
| 8 | Gujarati | Gujarati | 19 | Maithili | Devanagari |
| 9 | Punjabi | Gurmukhi | 20 | Manipuri | Bengali |
| 10 | Urdu | Arabic | 21 | Sanskrit | Devanagari |
| 11 | Assamese | Bengali | 22 | Santali | Ol Chiki |

---

## 🎛️ Two Input Modes

### 🎤 Mode 1: Microphone (In-Person Events)
Connect any microphone. Speak. Captions appear on all phones.
- Best for: conferences, classrooms, seminars, physical events.
- VAD threshold auto-raised to 0.65 to suppress earphone/earbud static.

### 💻 Mode 2: System Audio / Loopback (Online Events)
Captures audio playing on the laptop — Zoom, Meet, YouTube, news, etc.
- Uses **VB-Audio Virtual Cable** (free virtual audio device).
- Best for: hybrid events, online lecture translation, broadcast monitoring.
- Zero microphone bleed — cleaner audio = higher accuracy.

---

## 👥 Host vs. Viewer — Role-Based Interface

| | Host (Laptop) | Viewer (Phone) |
|--|--|--|
| **Access via** | `localhost:8080` | `192.168.137.1:8080` |
| **Start / Stop pipeline** | ✅ Yes | ❌ No (auto-syncs with host) |
| **Change own language** | ✅ Yes | ✅ Yes |
| **Caption display** | ✅ Full UI | ✅ Full UI |
| **Welcome screen text** | "Ready to start" | "Waiting for Host..." |

The moment the host clicks **Start**, every viewer phone automatically activates and begins receiving captions. No manual action from viewers required.

---

## 📊 Performance

| Configuration | Latency | CPU Load |
|--------------|---------|---------|
| English only (no translation) | **~0.6s** | ~15% |
| 1 Indian language | **~0.9s** | ~30% |
| 2 Indian languages | **~1.2s** | ~45% |
| 4 Indian languages (max) | **~1.8s** | ~70% |
| With NVIDIA GPU | **~0.3s** | Minimal |

> **500 people watching? CPU load is the same as 4 people — because only unique languages are translated.**

---

## 🔮 Architecture Scalability — SoC Ready

The codebase is **hardware-agnostic by design**. It runs identically on:

| Platform | Backend | Status |
|----------|---------|--------|
| Intel/AMD Laptop CPU | CTranslate2 INT8 | ✅ Production Ready |
| NVIDIA GPU (CUDA) | CTranslate2 FP16 | ✅ Auto-detected |
| Qualcomm / Rockchip SoC | ONNX Runtime (NPU) | 🔧 Architecture Ready |
| NVIDIA Jetson Nano | TensorRT | 🔧 Architecture Ready |
| Raspberry Pi 5 | ONNX Runtime | 🔧 Architecture Ready |

Only the **inference backend** changes. All WebSocket, translation logic, and UI remain identical.

---

## 🚀 How to Demo — Live Setup in 3 Minutes

### Step 1: Start the Server
```
python web_server.py
```
Models load in ~10 seconds. Then the server is ready.

### Step 2: Create the Network
> **With a router:** Connect laptop + phones to same Wi-Fi.  
> **Without a router:** Enable Windows Mobile Hotspot. Phones connect to your laptop's hotspot.

### Step 3: Phones Open the App
Phones open: `http://192.168.137.1:8080`  
No app download. No login. Instant UI in the browser.

### Step 4: Each Phone Picks Their Language
Judge 1 → Hindi. Judge 2 → Tamil. Judge 3 → Telugu.

### Step 5: Click Start on Laptop
Speak. Every phone gets live captions in their chosen language instantly.

---

## 📁 Project Structure

```
PolyVerba/
│
├── web_server.py              ← FastAPI server, WebSocket routing, multicast
│
├── stt/
│   ├── system_audio.py        ← Dual-thread pipeline, VAD, multicast translator
│   ├── whisper_engine.py      ← Faster-Whisper STT (INT8, auto GPU/CPU)
│   └── translate.py           ← FLORES codes for all 22 languages
│
├── translation/
│   └── nllb_engine.py         ← Meta NLLB-600M translation (INT8 quantized)
│
├── web/
│   ├── templates/index.html   ← Glassmorphism UI (Jinja2)
│   └── static/
│       ├── style.css          ← Animations, dimming, Indic fonts
│       └── app.js             ← WebSocket client, Host/Viewer logic, auto-sync
│
├── models/                    ← Local AI model cache (offline-safe)
├── .env                       ← HF_HUB_OFFLINE=1 (zero cloud calls)
└── requirements.txt           ← All Python dependencies
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **STT Engine** | Faster-Whisper (CTranslate2) | Speech-to-text, INT8 quantized |
| **VAD** | Silero VAD | Silence suppression, noise filtering |
| **Translation** | Meta NLLB-200-600M | 22+ language neural machine translation |
| **Inference Runtime** | CTranslate2 | Optimized INT8/FP16 transformer inference |
| **Web Server** | FastAPI + uvicorn | REST API + WebSocket server |
| **Real-time Delivery** | Starlette WebSockets | Push-based caption streaming |
| **Audio Capture** | SoundCard (WASAPI) | Mic + loopback capture on Windows |
| **Resampling** | SciPy resample_poly | Anti-aliased 44.1kHz → 16kHz |
| **UI** | Vanilla HTML/CSS/JS | Zero-dependency, mobile-first |
| **Fonts** | Google Noto Sans Indic | All 22 Indian script families |

---

<div align="center">

---

## The Vision

> *PolyVerba turns any laptop into an offline edge AI broadcast tower.*  
> *One device serves hundreds. Every person hears in their own language.*  
> *No internet. No app. No compromise.*

---

**Built for the edge. Designed for inclusion. Engineered for India.**

*Powered by Faster-Whisper · Meta NLLB-600M · FastAPI · WebSockets*

</div>
