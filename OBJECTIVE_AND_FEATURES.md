# PolyVerba: Objectives & Features

## Objective
Develop a production-grade, real-time speech-to-text platform optimized for live physical events and online webinars. The system must hit sub-1-second latency targets while supporting 12 official Indian languages. It must dynamically arbitrage between Cloud APIs (Sarvam AI/Custom GPUs) and local Edge AI (INT16 Quantized CPU processing) to survive event Wi-Fi blackouts.

## Core Features (Hackathon "Worst-Case Device" Edition)

### 1. Unified Event Interface (React + Vite)
- We use a single, unified dark-mode UI replacing the complex Daily/Event modes.
- **Organizer View:** Full dashboard containing Latency Telemetry graphs (Chart.js) and QR Code generators when accessed via the host's localhost.
- **Audience View:** Minimalist, sleek UI. The audience scans a QR code, accesses the WebApp via LAN Wi-Fi, and selects their Target Language from a dropdown.

### 2. 3-Tier Arbitration Architecture
- **Tier 1 (Custom Cloud):** Custom-hosted GPUs for maximum speed.
- **Tier 2 (Commercial Backup):** Sarvam AI streaming endpoints.
- **Tier 3 (True Edge Offline):** Completely offline `INT16` or `FP16` optimized `faster-whisper` and `AI4Bharat` via `CTranslate2` mapped purely to the laptop's CPU to survive total internet failure.

### 3. Universal Loopback Audio Capture
- Captures simultaneous streams: The physical Stage Microphone (via `pyaudio`) AND Internal Desktop Audio (via `soundcard`). 
- Enables PolyVerba to translate live YouTube streams, Zoom webinars, or Netflix movies natively without routing external cables.

### 4. Dynamic Zero-Shot RAG Vocabulary
- Automatically extracts new Proper Nouns (PROPN) via the `spaCy` NLP named-entity recognition pipeline.
- Instantly injects obscure medical or technical acronyms into Whisper's 'hotwords' dictionary in real-time without the Organizer manually typing them.

### 5. Continuous Speaker Diarization
- Uses `pyannote.audio` local voiceprint clustering to dynamically tag overlapping speakers without pre-training identities.
- Automatically prepends `[Speaker 1]` and `[Speaker 2]` to the transcription strings during Q&A sessions.

### 6. Lazy Pub/Sub Translation
- To conquer the CPU hardware limits of Edge laptops, the backend actively tracks WebSocket user target languages.
- It only translates audio into the specific languages the audience is actually requesting, saving massive CPU thermal bandwidth.
