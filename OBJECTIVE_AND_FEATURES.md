<div align="center">

# 🌐 PolyVerba
**A live-event multilingual translation matrix bridging zero-downtime Edge AI and Cloud APIs.**

[![Architecture](https://img.shields.io/badge/Architecture-3--Tier_Arbitration-blue?style=for-the-badge)](#)
[![Fault Tolerance](https://img.shields.io/badge/Fault_Tolerance-100%25_Offline_Edge-success?style=for-the-badge)](#)
[![Data Pipeline](https://img.shields.io/badge/Data_Pipeline-Zero--Shot_Semantic_Extraction-purple?style=for-the-badge)](#)

<p align="center">
  <i>Engineered for extreme hardware survivability, infinite cloud-scaling, and live linguistic accuracy.</i>
</p>

</div>

---

## 🎯 Executive Objective

> **To eradicate the live-event latency barrier and overcome critical venue infrastructure failures via dynamic localized routing.**

PolyVerba represents a fundamental shift in how concurrent multilingual speech-to-text is processed. Traditional software is tethered strictly to either heavy cloud computing—which fails catastrophically during ISP disruptions—or localized hardware, which thermally throttles under multi-language computational loads. 

By constructing a proprietary **Dynamic Routing Protocol**, PolyVerba actively arbitrages overlapping audio streams. It continuously routes between high-capacity elastic cloud instances and heavily-quantized local Edge AI hosted strictly on the speaker's machine. This guarantees uninterrupted, sub-second translation delivery across 12 Indian dialects, maintaining 100% hardware uptime and semantic integrity even through absolute network disintegration.

---

## 💎 Core Architecture & Capabilities

### 🛡️ 1. The 3-Tier Edge/Cloud Fallback System
Instead of relying on a single server, PolyVerba dynamically routes audio to the safest compute environment:
*   **Tier 1 (Private Cloud):** Uses massive custom servers for huge online audiences.
*   **Tier 2 (Commercial Backup):** Uses the Sarvam AI API for hyper-accurate fallback.
*   **Tier 3 (100% Offline Edge):** If the internet dies, the system instantly shifts back down to the laptop to run AI locally without web access.
**Tech Stack:** `AWS EC2`, `Sarvam AI API`, `FastAPI WebSockets`

### ⚖️ 2. Graceful CPU Pruning (Hardware Protection)
If the system falls back to the offline laptop (Tier 3), it cannot process all 12 languages at once without crashing the machine. The system scans the audience, locks in the **Top 6 most popular languages**, and turns off the rest to save the laptop's CPU from overheating.
**Tech Stack:** `CTranslate2 INT16 (faster-whisper & AI4Bharat)` 

### 🧠 3. Dual-Mode RAG (Custom Glossary Dictionary)
To prevent the AI from repeatedly misspelling complex medical or technical jargon during an event:
*   **Pre-Event:** Organizers upload slides to a local AI to pull out rare words.
*   **Live-Event:** An automatic zero-shot scanner catches new acronyms in real-time and injects them into the STT dictionary so they are spelled correctly moving forward.
**Tech Stack:** `Ollama LLM`, `spaCy (NER)`

### 🎙️ 4. Automatic Speaker Diarization
The system listens to the audio and automatically tags when different people are speaking (e.g., `[Speaker 1]`, `[Speaker 2]`). This is crucial for Q&A sessions where multiple voices overlap.
**Tech Stack:** `pyannote.audio`

### 📱 5. QR-Code Audience Interface
Attendees do not need to download an app. They scan a QR code shown on the projector, instantly join the local Wi-Fi, and select their preferred language from a beautiful dark-mode interface.
**Tech Stack:** `React`, `Vite`, `TailwindCSS`

### 🔇 6. Active Noise Cancellation
Before the AI even listens to the speaker, the system mathematically strips out background interference like venue Air Conditioners or audience chatter, completely eliminating "AI Hallucinations".
**Tech Stack:** `RNNoise (C-compiled bindings)`

### 🎛️ 7. Universal Audio Loopback Routing
The host can feed PolyVerba from physical stage microphones AND internal desktop audio simultaneously. This means PolyVerba can natively translate live Zoom meetings or YouTube videos without needing messy professional audio cables.
**Tech Stack:** `soundcard`, `pyaudio`

### ⏱️ 8. Predictive Slicing & Language Detection
PolyVerba automatically detects the speaker's language within seconds. To keep latency under 1-second, it slices audio into overlapping 400-millisecond chunks, translating instantly without chopping words in half.
**Tech Stack:** `faster-whisper VAD (Voice Activity Detection)` 

---
<div align="center">
  <i>This repository features proprietary edge-case survivability algorithms.</i>
</div>
