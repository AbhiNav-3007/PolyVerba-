# PolyVerba — Edge Backend Setup Guide

> Complete instructions to set up and run the PolyVerba backend on a Windows laptop.  
> **This guide covers backend only.** The frontend (HTML/CSS/JS in `web/`) requires no build step — it is served automatically by the FastAPI server.

---

## System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 | Windows 11 |
| RAM | 8 GB | 16 GB |
| CPU | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7 |
| Python | 3.10 | 3.10 |
| Storage | 6 GB free | 10 GB free |
| Internet | Only during initial setup | Not required at runtime |

---

## Step 1 — Install Python 3.10

Download: https://www.python.org/downloads/release/python-31011/

During installation: ✅ Check **"Add Python to PATH"**

Verify:
```powershell
python --version
# Must show: Python 3.10.x
```

---

## Step 2 — Install VB-Cable (Audio Routing)

VB-Cable creates a virtual audio device so PolyVerba can capture system audio from Zoom, YouTube, Teams, etc.

1. Download: https://vb-audio.com/Cable/
2. Extract ZIP → Run `VBCABLE_Setup_x64.exe` as **Administrator**
3. Reboot when prompted

**Configure Windows Audio after install:**

```
Win + R → type: mmsys.cpl → Enter
```

- **Playback tab:** Right-click `CABLE Input (VB-Audio)` → Set as Default Device
- **Recording tab:** Confirm `CABLE Output (VB-Audio)` appears — PolyVerba auto-detects it

**Optional — Hear audio through speakers while PolyVerba captions:**
```
Recording tab → Right-click CABLE Output → Properties → Listen tab
→ Check "Listen to this device" → set Playback to your Speakers → OK
```

---

## Step 3 — Create Virtual Environment

Navigate to the project folder:

```powershell
cd "d:\STUDY MATERIAL\PROJECTS\POLYVERBA - self"
```

Create and activate the virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt.

---

## Step 4 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

> ⚠️ This downloads ~2 GB including `torch`, `faster-whisper`, and `transformers`. Allow 10–20 minutes on first run.

---

## Step 5 — Download AI Models (One-Time)

### Whisper STT Model

Downloaded automatically on first use. To pre-download:

```powershell
venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; WhisperModel('base.en', device='cpu', compute_type='int8')"
```

| Model | Size | Speed | Use |
|---|---|---|---|
| `base.en` | ~150 MB | Fastest | English audio only |
| `small` | ~480 MB | Moderate | Auto language detection |

### IndicTrans2 Translation Model

```powershell
venv\Scripts\python.exe -c "from translation.indictrans_engine import IndicTransEngine; IndicTransEngine()"
```

Downloads `ai4bharat/indictrans2-en-indic-dist-200M` (~800 MB) to the HuggingFace cache.

> Both models are stored in `%USERPROFILE%\.cache\huggingface\hub\` and are reused every run.

---

## Step 6 — Run the Server

**Option A — One-click launcher:**
```powershell
.\run.bat
```

**Option B — Manual:**
```powershell
venv\Scripts\python.exe web_server.py
```

Expected output:
```
[STARTUP] Freed port 8080 (killed PID 0)

=======================================================
  PolyVerba - Edge Multilingual Captioning System
  -----------------------------------------------
  Open in browser:  http://localhost:8080
  Press Ctrl+C to stop the server
=======================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

Open **http://localhost:8080** in your browser. The UI loads immediately.

---

## Step 7 — First Run

1. Press **Start** in the browser UI
2. Wait ~12–15 seconds on first run (models loading into RAM)
3. On subsequent runs: models load in ~3s
4. Play audio from any application → captions appear in ~3–4 seconds

> Press **Ctrl+C** in the terminal to stop the server.

---

## Troubleshooting

**Port 8080 already in use:**
The server auto-kills the old process on startup. If it still fails:
```powershell
netstat -ano | findstr :8080
taskkill /PID <pid_from_above> /F
```

**VB-Cable not found:**
- Confirm `CABLE Input` is set as default Windows playback device
- Restart Windows Audio: `services.msc → Windows Audio → Restart`

**"Listening..." but no captions appear:**
- Confirm VB-Cable is routing audio (open YouTube and verify sound plays)
- Check terminal for `[STT ERROR]` or `[PROCESS ERROR]` lines

**Hindi works but Kannada/Tamil text looks wrong:**
The `dist-200M` model outputs phonetically correct content in Devanagari for Dravidian languages. This is a model capacity limitation, fixed in the planned Cloud deployment with the `1B` model.

---

## File Structure (Backend)

```
POLYVERBA - self/
├── web_server.py              ← FastAPI server entry point
├── run.bat                    ← One-click start
├── requirements.txt           ← Python dependencies
├── stt/
│   ├── whisper_engine.py      ← Whisper INT8 wrapper
│   ├── system_audio.py        ← Dual-thread audio pipeline
│   └── translate.py           ← FLORES-200 language code map
└── translation/
    └── indictrans_engine.py   ← IndicTrans2 translation wrapper
```

The `web/` directory (HTML, CSS, JS) requires no setup — served directly by FastAPI.
