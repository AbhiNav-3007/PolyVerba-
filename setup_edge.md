# PolyVerba — Universal Setup Guide (CPU & NVIDIA GPU)

PolyVerba runs on any Windows laptop. The **same codebase** auto-detects your hardware and selects the best configuration automatically — no manual code edits needed per machine.

| Hardware | Whisper Model | Meta NLLB-600M Model | Expected Latency |
|---|---|---|---|
| CPU (any laptop) | `base` (multilingual, int8) | `en-indic dist-200M` | ~1.2s |
| NVIDIA GPU (CUDA) | `medium` (float16) | `en-indic 1B` + `indic-en` + `indic-indic` | ~0.6s |

---

## Prerequisites

Ensure these are available before starting:

- **Python 3.10** — must be exactly 3.10 (ML libraries are not compatible with 3.11+)
- **Git for Windows** — required for HuggingFace CLI to store tokens correctly on Windows
- **VB-Cable** — virtual audio device to capture system audio from Chrome, Zoom, etc.
- **FFmpeg** — required by Whisper for audio decoding

---

## Step 0 — Get The Project (Git Clone)

```powershell
git clone https://github.com/AbhiNav-3007/PolyVerba-.git PolyVerba
cd PolyVerba
```

---

## Step 1 — Install & Configure VB-Cable (Audio Routing)

PolyVerba captures audio from any app (YouTube, Zoom, Teams) by routing it through a virtual cable. Without this, the system has no audio source.

1. Download VB-Cable from: https://vb-audio.com/Cable/
2. Extract the ZIP, right-click `VBCABLE_Setup_x64.exe` → **Run as Administrator**. Restart PC if prompted.
3. Open Sound settings: `Win + R` → type `mmsys.cpl` → Enter.
4. **Playback tab:** Right-click `CABLE Input` → **Set as Default Device**.
5. **Recording tab:** Right-click `CABLE Output` → **Set as Default Device**.
6. **To still hear audio through your speakers/headphones:**
   - Recording tab → right-click `CABLE Output` → Properties → **Listen** tab
   - Check *"Listen to this device"* → select your physical Speakers/Headphones → Apply.

> ⚠️ **Volume keys stopped working?** After VB-Cable install, Windows routes volume keys to the virtual cable. Fix:
> - `Settings → System → Sound → App volume and device preferences`
> - Set the specific app (e.g., Chrome) output to `CABLE Input (VB-Audio)`
> - Set `Realtek Audio` (or your speakers) back as the Windows default playback device
> - Volume keys now work normally, and PolyVerba continues capturing audio.

---

## Step 2 — Install FFmpeg

1. Download a pre-compiled Windows FFmpeg build from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the archive.
3. Add the `bin` folder (containing `ffmpeg.exe`) to your system **PATH** environment variable.
4. Open a new terminal and verify:
```powershell
ffmpeg -version
```

---

## Step 3 — Create Virtual Environment

Navigate to the project folder in PowerShell, then:

```powershell
py -3.10 -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt. If activation fails with a security error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 4 — Install PyTorch (Hardware-Specific)

This is the most important step. You must install the PyTorch version that matches your hardware.

### Check if you have an NVIDIA GPU

```powershell
nvidia-smi
```

- If this command works and shows a GPU table → you have a CUDA-capable GPU. Note the **CUDA Version** shown in the top-right of the table.
- If this command fails or says "not recognized" → CPU-only laptop. Skip to Option B.

---

### Option A — NVIDIA GPU (Recommended for speed)

**If your CUDA Version is 11.8:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**If your CUDA Version is 12.1 or newer:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify the GPU installation:
```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```
Expected output: `CUDA available: True`

---

### Option B — CPU Only (Standard laptop)

```powershell
pip install torch torchvision torchaudio
```

---

## Step 5 — Install Remaining Dependencies

Run these for **both CPU and GPU users**:

```powershell
# Core ML dependencies
pip install transformers==4.37.2 sentencepiece sacremoses indic-nlp-library accelerate

# Audio capture (44100Hz native capture + quality resampling)
pip install faster-whisper soundcard sounddevice numpy scipy ffmpeg-python

# Web server
pip install fastapi uvicorn jinja2 websockets python-multipart psutil
```

> ⚠️ `transformers==4.37.2` is pinned — do not upgrade, it breaks IndicTrans2 compatibility.
> Total download size is approximately **2–4 GB**. Allow 15–25 minutes on first install.

---

## Step 6 — HuggingFace Authentication (For Translation Models)

PolyVerba's translation models are hosted on HuggingFace as gated repositories. You must accept the usage terms and authenticate before they can download.

### Accept model terms (one-time, do this in browser)

Visit each model page and click **"Agree and access repository"**:

1. **en-indic 200M (CPU):** https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M
2. **en-indic 1B (GPU):** https://huggingface.co/ai4bharat/indictrans2-en-indic-1B
3. **indic-en 200M:** https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M
4. **indic-indic 320M:** https://huggingface.co/ai4bharat/indictrans2-indic-indic-dist-320M

> These models enable translation from English to Indian languages, Indian languages to English, and between Indian languages (e.g., Hindi → Tamil). Only the models needed for your translation direction are downloaded on first use.

### Generate an Access Token

1. Go to https://huggingface.co → Settings → **Access Tokens**
2. Click **New token** → select **Read** → copy the token.

### Login via CLI

```powershell
huggingface-cli login
```

Paste your token when prompted (it will be invisible). Press Enter.

> ⚠️ If you see `WinError 2`: Git for Windows is not installed or not on PATH. Install from https://git-scm.com/download/win then retry.

---

## Step 7 — Run The Application

```powershell
python web_server.py
```

Open your browser and go to: **http://localhost:8080**

The server will print which hardware it detected and which models it loaded:
```
[STARTUP] Hardware detected: GPU (CUDA)
[STARTUP] Pre-loading Whisper 'medium' + Meta NLLB-600M engines...
[STARTUP] Models ready on GPU (CUDA) — Start button is now instant!
```
or on CPU:
```
[STARTUP] Hardware detected: CPU
[STARTUP] Pre-loading Whisper 'base' + Meta NLLB-600M engines...
[STARTUP] Models ready on CPU — Start button is now instant!
```

> **First run only:** Models download automatically from HuggingFace (~800MB for 200M, ~4GB for 1B on GPU). This is a one-time download. All subsequent runs load from local cache in seconds.

---

## Step 8 — Verify Runtime Mode

Check the terminal output after pressing **Start**:
- `[STT] Device: CUDA | Precision: FLOAT16` → running on GPU ✅
- `[STT] Device: CPU  | Precision: INT8`   → running on CPU ✅

You can also verify manually:
```powershell
python -c "import torch; print('cuda available =', torch.cuda.is_available())"
```

On GPU: open Task Manager (`Ctrl+Shift+Esc`) → Performance → GPU → watch **Dedicated GPU Memory** spike when you press Start.

---

## Supported Input Modes

| Mode | Description | Best For |
|---|---|---|
| **English** | Lightweight English model, fastest | English-only lectures/meetings |
| **Auto-Detect** | Detects speaker language automatically | Multilingual content, Hindi/Tamil input |

---

## Supported Output Languages

PolyVerba can translate into:

**Hindi, Marathi, Bengali, Gujarati, Punjabi, Tamil, Telugu, Kannada, Malayalam, Urdu, Nepali, Assamese, Odia**

> On **GPU**: all languages print in their correct native script (Tamil → தமிழ், Kannada → ಕನ್ನಡ) using the 1B model.
> On **CPU**: Hindi, Marathi, Bengali, Gujarati, Punjabi, Urdu, Assamese, Nepali print in correct script. Tamil/Telugu/Kannada/Malayalam may show partially transliterated output (limitation of the CPU 200M model).

---

## Latency Expectations

| Stage | CPU | GPU |
|---|---|---|
| Model loading (first run) | 15–20 seconds | 25–40 seconds |
| Model loading (cached) | 2–3 seconds | 3–5 seconds |
| Speech → first caption | ~1.2 seconds | ~0.6 seconds |

---

## Troubleshooting

**"Listening" but no captions appear:**
- Confirm `CABLE Input` is set as default Playback device in `mmsys.cpl`
- Confirm audio is actually playing in another app
- Check terminal output for `[RECORDER ERROR]` messages

**Port 8080 already in use:**
```powershell
netstat -ano | findstr :8080
taskkill /PID <PID shown> /F
```
Then restart the server. PolyVerba also auto-kills port 8080 on startup if it detects a conflict.

**GPU laptop still showing CPU in terminal:**
1. Confirm `nvidia-smi` works in terminal.
2. Run: `python -c "import torch; print(torch.cuda.is_available())"` — must show `True`.
3. If it shows `False`, reinstall the matching CUDA PyTorch wheel (Step 4, Option A).
4. Do NOT run `pip install torch` without the `--index-url` flag — it installs CPU-only torch.

**HuggingFace login fails with WinError 2:**
Install Git for Windows from https://git-scm.com/download/win, then retry `huggingface-cli login`.

**`venv\Scripts\activate` fails with security error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**IndicTrans2 1B model download is very slow:**
The 1B model is ~4GB. Use a good internet connection. It downloads once and is cached permanently at `C:\Users\<you>\.cache\huggingface\hub\`.
