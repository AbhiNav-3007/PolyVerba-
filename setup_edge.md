# PolyVerba Universal Setup Guide (CPU & NVIDIA GPU)

This guide details how to set up the PolyVerba project from scratch on a new Windows machine. It covers system-level audio routing, Python ML dependencies, HuggingFace authentication, and running the application.

---

## Prerequisites

Before you start, ensure the following are available on your machine (Windows 10/11 assumed):

- **Python 3.10** — This specific version is required to avoid compatibility issues with the ML libraries used.
- **Git for Windows** — Required for HuggingFace CLI authentication to store tokens correctly on Windows.
- **VB-Cable** — Used to route system audio (from Chrome, Zoom, etc.) into a virtual recording device that PolyVerba can capture.
- **FFmpeg** — Required by the Whisper STT engine for audio decoding.

---

## Step 1 — Install & Configure VB-Cable (Audio Routing)

PolyVerba captures your computer's system audio by routing it through a virtual audio cable — so it can process audio from any application (YouTube, Zoom, Teams, etc.) without using a physical microphone.

1. Download and install VB-Cable from: https://vb-audio.com/Cable/
2. Run `VBCABLE_Setup_x64.exe` as Administrator and restart your PC.
3. Open Windows Sound Settings: `Win + R` → type `mmsys.cpl` → hit Enter.
4. **Playback tab:** Right-click `CABLE Input` → **Set as Default Device**.
5. **Recording tab:** Right-click `CABLE Output` → **Set as Default Device**.
6. **To still hear audio:** On the Recording tab → right-click `CABLE Output` → Properties → **Listen** tab → check *"Listen to this device"* → select your physical Speakers/Headphones → Apply.

---

## Step 2 — Install FFmpeg

1. Download a pre-compiled Windows FFmpeg build from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the archive.
3. Add the `bin` folder (containing `ffmpeg.exe`) to your system's **PATH** environment variable.
4. Open a new terminal and verify: `ffmpeg -version`

---

## Step 3 — Project Setup (Virtual Environment)

Open your terminal (PowerShell or Command Prompt) and navigate to the project directory.

**Create the virtual environment** using Python 3.10:
```powershell
py -3.10 -m venv venv
```

**Activate the environment:**
```powershell
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt. If activation fails with a security error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 4 — Install PyTorch & Dependencies

With the virtual environment activated, we first need to install PyTorch. This depends on whether your laptop has a dedicated NVIDIA GPU.

**Option A: If you have an NVIDIA GPU (Recommended for speed)**
1. Check your CUDA version by typing `nvidia-smi` in terminal.
2. If CUDA is 11.8:
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. If CUDA is 12.1+:
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

**Option B: If you DO NOT have an NVIDIA GPU (Standard laptop)**
```powershell
pip install torch torchvision torchaudio
```

**Next, install the remaining packages (for both CPU and GPU users):**
```powershell
# Core ML dependencies
pip install transformers==4.37.2 sentencepiece sacremoses indic-nlp-library accelerate

# Audio capture and Whisper
pip install faster-whisper soundcard sounddevice numpy scipy ffmpeg-python

# Web server
pip install fastapi uvicorn jinja2 websockets python-multipart psutil
```

> ⚠️ `transformers==4.37.2` is a pinned version required for IndicTrans2 compatibility.
> Total download size is approximately 2–4 GB. Allow 15–25 minutes on first install.

---

## Step 5 — HuggingFace Authentication (For Translation Model)

The translation model used by PolyVerba is hosted on HuggingFace as a gated repository. You must authenticate before it can be downloaded.

1. Go to https://huggingface.co and create a free account.
2. Visit the model page for `ai4bharat/indictrans2-en-indic-dist-200M` and agree to the usage terms.
3. Go to your HuggingFace Settings → **Access Tokens** → generate a new **Read** token.
4. In your terminal (with Git installed), run:
```powershell
huggingface-cli login
```
5. Paste your token when prompted (it will be invisible) and press Enter.

> ⚠️ If you see `WinError 2`, Git is not installed or not on your PATH. Install Git for Windows first.

The model (~800 MB) will download automatically on the first run and will be cached for all future runs.

---

## Step 6 — Running the Application

**Option A: Web Interface (Recommended)**

Make sure your virtual environment is activated, then run:
```powershell
python web_server.py
```
Open your browser and go to: http://localhost:8080

Play any system audio (YouTube, Zoom, etc.), select your source and target languages, and press **Start**.

**Option B: One-Click Launch**

Double-click `run.bat` in the project folder to start the server without opening a terminal manually.

---

## Supported Input Modes

- **English Only** — Uses a lightweight English-only model for faster processing. Best for English-language content.
- **Auto-Detect** — Uses a multilingual model that detects the speaker's language automatically. Supports Hindi, Tamil, Telugu, and more as input.

---

## Supported Output Languages

PolyVerba can translate live speech into the following Indian languages:

Hindi, Marathi, Bengali, Gujarati, Punjabi, Tamil, Telugu, Kannada, Malayalam, Urdu, Assamese, Nepali, Odia

---

## Latency Expectations

| Stage | Approximate Time |
|---|---|
| Model loading (first run) | 12–15 seconds |
| Model loading (subsequent runs) | 2–3 seconds |
| Speech → first caption words | 3–4 seconds |
| End-to-end steady state | ~1.5 seconds |

---

## Troubleshooting

**Port 8080 already in use:**
```powershell
netstat -ano | findstr :8080
taskkill /PID <PID number shown> /F
```
Then restart the server.

**"Listening" but no captions appear:**
- Confirm `CABLE Input` is set as default Playback device in `mmsys.cpl`
- Confirm audio is actually playing in another app
- Check terminal output for any error messages

**Volume keys stopped working after VB-Cable install:**
VB-Cable becomes the default playback device, so volume keys control the virtual cable (which has no physical volume). Fix:
- Go to `Settings → System → Sound → App volume and device preferences`
- Set the specific app (e.g., Chrome) output to `CABLE Input (VB-Audio)`
- Then set `Realtek Audio` (or your physical speakers) back as the Windows default playback device
- Volume keys will now work normally, and PolyVerba continues to capture audio correctly

**`venv\Scripts\activate` fails with security error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**HuggingFace login fails with WinError 2:**
Install Git for Windows from https://git-scm.com/download/win, then retry `huggingface-cli login`.
