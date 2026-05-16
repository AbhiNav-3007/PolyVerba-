<div align="center">

<img src="https://img.shields.io/badge/PolyVerba-Edge%20AI-6D28D9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMgMkwzIDE0aDlsLTEgOCAxMC0xMmgtOWwxLTh6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==" alt="PolyVerba">

# PolyVerba

### Real-Time Multilingual Captioning — 100% Offline Edge AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Whisper](https://img.shields.io/badge/Faster--Whisper-STT-412991?style=flat-square)](https://github.com/guillaumekln/faster-whisper)
[![NLLB](https://img.shields.io/badge/Meta_NLLB-600M-1877F2?style=flat-square)](https://huggingface.co/facebook/nllb-200-distilled-600M)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**One speaker. Any language. Every device. No internet.**

*A laptop runs a local AI server. Hundreds of phones connect over Wi-Fi. Each person reads captions in their own language. No internet. No app download. No cost.*

</div>

---

## 🔴 The Problem

India has 22 official languages. Most live events have only one. Every day, in conferences, colleges, Parliament sessions, and civic meetings across India — millions of people sit in silence because the speaker isn't using their language.

Commercial tools are either **English-only**, **cloud-dependent**, or **too expensive** for academic and civic events. **PolyVerba solves this entirely on a standard laptop CPU, with zero internet.**

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔒 **100% Offline** | All AI runs locally. Zero internet after first model download. |
| 📡 **Personal AI Broadcast** | Laptop acts as a local AI server. Phones connect over Wi-Fi hotspot. |
| 🌍 **22+ Indian Languages** | All official Indic scripts — Devanagari, Tamil, Telugu, Bengali, Ol Chiki and more. |
| 📱 **Per-Device Language Selection** | Each phone independently picks its own language. 4 different languages, 4 different phones, one laptop. |
| ⚡ **~0.9s Latency** | Whisper STT (~0.6s) + NLLB translation (~0.3s) + WebSocket delivery (~5ms). |
| 👥 **500+ Device Scalability** | CPU scales with unique languages (max 4), NOT number of connected devices. 500 phones = same CPU load as 4. |
| 🎤 **Dual Audio Input** | System Audio loopback (Zoom/YouTube/Meet) or Microphone (live events). |
| 🖥️ **Host / Viewer Roles** | Start/Stop only visible on the laptop. Phones auto-sync and show only captions + language selector. |
| 🎨 **Premium Glassmorphism UI** | Dark purple theme, animated word-by-word captions, progressive dimming, mobile-responsive. |

---

## 🏗️ Architecture

```
┌─────────────────────────── YOUR LAPTOP (EDGE SERVER) ──────────────────────────┐
│                                                                                 │
│  🎤 Audio Input        🤖 Faster-Whisper        🔁 Meta NLLB-600M              │
│  (Mic / VB-Cable) ──▶  STT Engine          ──▶  Translation Engine             │
│  44.1kHz → 16kHz       CTranslate2 INT8         CTranslate2 INT8               │
│  2s chunks, 1.3s step  Silero VAD               Up to 4 languages              │
│  ~0.6s latency         ~0.3s / language                                         │
│                                    │                                            │
│         FastAPI WebSocket Server  (http://192.168.137.1:8080)                  │
│         Routes each language to the correct phone via subscription map          │
└────────────────────────────────────┬───────────────────────────────────────────┘
                                     │  Wi-Fi (Mobile Hotspot / LAN Router)
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
       ┌──────▼──────┐       ┌───────▼─────┐       ┌───────▼─────┐
       │ 📱 Judge 1   │       │ 📱 Judge 2   │       │ 📱 Judge 3   │
       │   Hindi      │       │   Tamil      │       │   Telugu    │
       │ नमस्ते...    │       │ வணக்கம்...   │       │ నమస్కారం... │
       └─────────────┘       └─────────────┘       └─────────────┘
              Browser only — No app install. No account. No internet.
```

### Dynamic Subscription Multicast

The core innovation: the server translates only the **unique set of languages** being requested, not once per device.

```
Phone A subscribes → "Hindi"
Phone B subscribes → "Tamil"
Phone C subscribes → "Telugu"
Phone D subscribes → "Hindi"   ← same as Phone A

Server runs NLLB exactly 3 times (Hindi, Tamil, Telugu)
NOT 4 times. Phones A and D both get Hindi from one pass.

500 phones connected, all requesting Hindi/Tamil?
CPU still runs exactly 2 translation passes.
```

---

## 🌍 Supported Languages

All 22 official Indian languages + English:

| | Language | Script | | Language | Script |
|--|----------|--------|--|----------|--------|
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

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **STT** | `faster-whisper` (CTranslate2) | Speech-to-text, INT8 quantized, CPU/GPU auto |
| **VAD** | Silero VAD (built-in) | Silence suppression, noise filtering |
| **Translation** | Meta NLLB-200-600M | 22+ language neural machine translation |

> **Alternative Translation Models:** You can swap NLLB-600M for `ai4bharat/indictrans2-en-indic-dist-200M` *(200M distilled, via `pip install indic-nlp-library` — handles all 22 Indian scripts natively)* or `ai4bharat/indictrans2-en-indic-1B` *(1B, highest accuracy, GPU recommended)*. See [`translation/nllb_engine.py`](translation/nllb_engine.py) for swap instructions.
| **Inference** | CTranslate2 | Optimized INT8/FP16 transformer runtime |
| **Web Server** | FastAPI + uvicorn | REST API + WebSocket server |
| **Streaming** | Starlette WebSockets | Push-based real-time caption delivery |
| **Audio** | SoundCard (WASAPI) | Mic + loopback capture on Windows |
| **Resampling** | SciPy resample_poly | Anti-aliased 44.1kHz → 16kHz conversion |
| **UI** | Vanilla HTML/CSS/JS | Zero-dependency, mobile-first |
| **Fonts** | Google Noto Sans Indic | All 22 Indian script families |

---

## 📋 Prerequisites

- **OS:** Windows 10/11
- **Python:** 3.10 or 3.12
- **RAM:** 4 GB minimum (8 GB recommended)
- **Storage:** ~2 GB for AI models
- **Audio:** [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) *(for System Audio / Loopback mode)*

> **GPU (Optional):** If NVIDIA GPU with CUDA is detected, PolyVerba automatically upgrades to FP16 precision and Whisper `medium` — reducing latency to ~0.3s.

---

## 🚀 Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/PolyVerba.git
cd PolyVerba
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download AI Models

```bash
# Downloads Whisper and NLLB-600M and converts to CTranslate2 INT8 format
python convert_nllb.py
```

> This only needs to run **once**. Models are cached in the `/models` directory. After this, the system runs 100% offline.

### Step 5 — (Optional) Install VB-Audio Virtual Cable

Required for **System Audio / Loopback** mode (translating Zoom calls, YouTube, etc.):
1. Download from [vb-audio.com/Cable](https://vb-audio.com/Cable/)
2. Install and restart your PC
3. Set `CABLE Input` as your default playback device in Windows Sound settings

---

## ▶️ Running PolyVerba

```bash
python web_server.py
```

The server starts and is accessible at:

| Device | URL |
|--------|-----|
| **Your Laptop** | `http://localhost:8080` |
| **Phone (via Hotspot)** | `http://192.168.137.1:8080` |
| **Phone (via Router)** | `http://[your-wifi-ip]:8080` |

To find your Wi-Fi IP: Open PowerShell → `ipconfig` → Look for **IPv4 Address** under Wireless LAN adapter.

---

## 📡 Live Demo Setup (Judges / Presentation)

### With Windows Mobile Hotspot (No Router Needed)

1. **Settings → Network & Internet → Mobile Hotspot** → Turn ON
2. Start PolyVerba: `python web_server.py`
3. Ask judges to connect phones to your laptop's hotspot Wi-Fi
4. Judges open `http://192.168.137.1:8080` in their phone browser
5. Each judge selects their preferred language from the dropdown
6. Click **Start** on your laptop — all phones instantly receive live captions!

### Firewall Rule (Run Once as Admin)

If phones show "connecting" or "timed out":

```powershell
New-NetFirewallRule -DisplayName "PolyVerba" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow -Profile Any
```

---

## 🖥️ Usage Guide

### Host (Laptop)
- Navigate to `http://localhost:8080`
- Select **Audio Source**: System Audio (loopback) or Microphone
- Select your **language**
- Click **Start** — all viewer phones auto-activate
- Click **Stop** to end the session

### Viewer (Phone)
- Connect to the same Wi-Fi as the laptop
- Open `http://192.168.137.1:8080` in browser
- Select your preferred language from the **🌐 Language** dropdown at the bottom bar
- Use **▶ Show** / **⏸ Pause** to control your own caption display
- Start/Stop buttons are hidden — the host controls the session

---

## 📁 Project Structure

```
PolyVerba/
│
├── web_server.py              # FastAPI server — REST API, WebSocket, multicast routing
│
├── stt/
│   ├── system_audio.py        # Dual-thread pipeline — recorder + processor + multicast
│   ├── whisper_engine.py      # Faster-Whisper STT (INT8, auto GPU/CPU detection)
│   └── translate.py           # FLORES-200 language code mappings for all 22 languages
│
├── translation/
│   └── nllb_engine.py         # Meta NLLB-600M engine (INT8 quantized via CTranslate2)
│                               # Alternative: ai4bharat/indictrans2-en-indic-dist-200M
│                               #              ai4bharat/indictrans2-en-indic-1B
│                               #  (both via `indic-nlp-library` — all 22 Indian scripts)
│
├── web/
│   ├── templates/index.html   # Glassmorphism UI (Jinja2 template)
│   └── static/
│       ├── style.css          # Animations, progressive dimming, Indic fonts, mobile bar
│       └── app.js             # WebSocket client, Host/Viewer logic, word animation
│
├── models/                    # Local model cache (auto-populated by convert_nllb.py)
├── convert_nllb.py            # One-time model download + CTranslate2 conversion script
├── .env                       # HF_HUB_OFFLINE=1 (zero cloud calls at runtime)
├── requirements.txt           # All Python dependencies
├── run.bat                    # One-click Windows launch
└── setup_edge.md              # Detailed setup guide
```

---

## ⚡ Performance

| Configuration | Latency | CPU Load |
|--------------|---------|---------|
| English only (no translation) | **~0.6s** | ~15% |
| 1 Indian language | **~0.9s** | ~30% |
| 2 Indian languages simultaneously | **~1.2s** | ~45% |
| 4 Indian languages (max) | **~1.8s** | ~70% |
| NVIDIA GPU (any config) | **~0.3s** | Minimal |

> **CPU Safety Cap:** Hard-limited to 4 simultaneous languages. The 5th unique language subscription is silently ignored to protect CPU budget. Future: "Capacity Reached" notification.

*Benchmarked on Intel Core i5 11th Gen, 8GB RAM, Windows 11*

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | Serves the main UI |
| `/api/start` | `POST` | Starts audio capture and translation pipeline |
| `/api/stop` | `POST` | Stops the pipeline |
| `/api/status` | `GET` | Returns `{ running, active_languages, capture_mode }` |
| `/ws/captions` | `WebSocket` | Persistent connection for real-time caption streaming |

### WebSocket Subscribe (Client → Server)
```json
{ "type": "subscribe", "language": "Hindi" }
```

### WebSocket Final Caption (Server → Client)
```json
{
  "type": "final",
  "text": "नमस्ते, आज हम बात करेंगे...",
  "latency": 0.92
}
```

---

## 🛡️ Why This Works Offline

1. **Models cached locally** — After first run, all AI weights live in `/models`. Zero internet needed.
2. **`HF_HUB_OFFLINE=1`** — Set in `.env`. Prevents any HuggingFace server ping at startup.
3. **Local web server** — Phones connect to your laptop's IP, not any cloud endpoint.
4. **Hardware agnostic** — Same codebase runs on CPU laptops and NVIDIA GPUs. Can be ported to AI SoCs (Qualcomm, Jetson) by swapping CTranslate2 for ONNX Runtime.

---

## 🔮 Future Scalability & Roadmap

| # | Feature | Status |
|---|---------|--------|
| F1 | Speaker Recognition & Diarization | 📋 Planned |
| F2 | Intelligent Acoustic Focus & Noise Isolation | 📋 Planned |
| F3 | Cloud Deployment & Hybrid Edge-Cloud Mode | 📋 Planned |
| F4 | Custom ML — Noise Cancellation & Diarization | 📋 Planned |
| F5 | Context-Aware Conversational AI Model | 📋 Planned |
| F6 | Colloquial Natural Language Translation | 📋 Planned |
| F7 | QR-Based Instant Joining (Zero IP Typing) | 🔧 In Progress |
| F8 | Universal Hardware Scalability & Native App | 📋 Planned |
| F9 | RAG-Based Dynamic Vocabulary Engine | 📋 Planned |
| F10 | Text-to-Speech & Speech-to-Speech Mode | 📋 Planned |
| F11 | PolyVerba Edge Earpiece (Hardware Product) | 💡 Vision |

### Highlights

- **F1 — Speaker Diarization:** Labels captions with speaker identity (`[Speaker 1]`, `[Speaker 2]`) using `pyannote.audio` — critical for debates, panels, and interviews.
- **F2 — Acoustic Focus:** A perceptual audio lens that dynamically isolates the target speaker's voice and suppresses crowd noise, AC hum, applause, and overlapping speech — tuned for Indian venue acoustics.
- **F4 — Custom ML Models:** Train PolyVerba's own noise cancellation and diarization models on Indian venue recordings rather than Western-optimized pretrained models.
- **F5 — Context AI:** A small fine-tuned LLM that tracks topic, entities, and domain vocabulary across the session — so "ISRO", "Rajya Sabha", "crore" are never misheard.
- **F6 — Conversational Translation:** Fine-tune NLLB / IndicTrans2 on movie subtitles and informal parallel corpora so translations sound like real spoken language, not textbooks.
- **F7 — QR Joining:** Audience scans a QR code on the projector — browser opens fully connected. No IP address, no typing, no app. Works offline.
- **F8 — Native App:** Single installable binary (`PyInstaller`) targeting <500MB including quantized models; runs on CPU, low-end GPU, high-end GPU, and Android edge devices.
- **F10 — Speech-to-Speech:** Phone earpiece speaks the translation in real time — Phase 1 via Web Speech API (zero install), Phase 2 via Microsoft Neural TTS voices (`hi-IN-SwaraNeural` etc.).
- **F11 — Edge Earpiece:** A self-contained wireless earpiece (Qualcomm QCC SoC) that runs the full pipeline — STT + translation + TTS — with no phone, no internet, and no cloud. Target cost: ₹2,000.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for the edge. Designed for inclusion. Engineered for India.**

*Powered by Faster-Whisper · Meta NLLB-600M · FastAPI · WebSockets*

*100% Offline · Zero Cloud Dependency · 22+ Indian Languages*

</div>
