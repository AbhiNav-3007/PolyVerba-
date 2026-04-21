# PolyVerba — Edge Setup Guide
> Complete step-by-step backend setup for the PolyVerba Edge AI captioning system on Windows.

---

## Before You Begin

**What you need:**
- Windows 10 or 11 laptop
- At least 8 GB RAM (16 GB recommended)
- At least 6 GB free disk space
- Internet connection (only during setup — not needed at runtime)

**What PolyVerba does after setup:**
- Runs 100% offline
- Translates live speech into 12 Indian languages in real time
- Opens in any browser at `http://localhost:8080`

---

## Step 1 — Install Python 3.10

> ⚠️ Must be Python 3.10 specifically. 3.11 and 3.12 are NOT compatible with all dependencies.

1. Go to: https://www.python.org/downloads/release/python-31011/
2. Download **Windows installer (64-bit)**
3. Run the installer
4. On the first screen: ✅ **Check "Add Python to PATH"** (very important)
5. Click **Install Now**

**Verify it worked:**
```powershell
python --version
```
Expected output: `Python 3.10.x`

---

## Step 2 — Install VB-Audio Virtual Cable

VB-Cable creates a virtual audio device so PolyVerba can capture audio from Zoom, YouTube, Teams, etc. without a microphone.

1. Go to: https://vb-audio.com/Cable/
2. Click **Download VB-CABLE Driver**
3. Extract the ZIP file
4. Right-click `VBCABLE_Setup_x64.exe` → **Run as Administrator**
5. Click **Install Driver**
6. **Restart your computer** when prompted

**Configure Windows Audio after restart:**

Press `Win + R` → type `mmsys.cpl` → press Enter

This opens Sound Settings:

- Go to **Playback tab** → right-click `CABLE Input (VB-Audio Virtual Cable)` → click **Set as Default Device**
- Go to **Recording tab** → confirm you can see `CABLE Output (VB-Audio Virtual Cable)`

**Optional — Hear audio through speakers while PolyVerba captions it:**
```
Recording tab → right-click CABLE Output → Properties
→ Listen tab → check "Listen to this device"
→ Playback through: your Speakers (e.g. Realtek Audio)
→ Click OK
```

---

## Step 3 — Download the Project

**Option A — If you have Git installed:**
```powershell
git clone https://github.com/AbhiNav-3007/PolyVerba-.git "POLYVERBA - self"
cd "POLYVERBA - self"
```

**Option B — Manual download:**
1. Go to the GitHub repository
2. Click green **Code** button → **Download ZIP**
3. Extract to your preferred location
4. Open that folder in PowerShell

---

## Step 4 — Create Python Virtual Environment

A virtual environment keeps PolyVerba's dependencies separate from your system Python.

Navigate to the project folder first:
```powershell
cd "d:\STUDY MATERIAL\PROJECTS\POLYVERBA - self"
```

Create the virtual environment:
```powershell
python -m venv venv
```

Activate it:
```powershell
venv\Scripts\activate
```

You should now see `(venv)` at the start of your command prompt. If you see an error about execution policy, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

---

## Step 5 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

> ⚠️ This downloads approximately 2–3 GB including PyTorch, faster-whisper, and transformers. Allow **15–25 minutes** on first run depending on your internet speed.

If you see any error during install, try:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 6 — Download AI Models (One-Time)

The models download automatically when you first start PolyVerba. But you can pre-download them to avoid waiting:

**Download Whisper STT model (base.en — ~150 MB):**
```powershell
venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; WhisperModel('base.en', device='cpu', compute_type='int8'); print('Whisper base.en ready')"
```

**Download Whisper STT model (small — ~480 MB, for auto language detection):**
```powershell
venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('Whisper small ready')"
```

**Download IndicTrans2 translation model (~800 MB):**
```powershell
venv\Scripts\python.exe -c "from translation.indictrans_engine import IndicTransEngine; IndicTransEngine(); print('IndicTrans2 ready')"
```

Models are saved to: `C:\Users\YourName\.cache\huggingface\hub\`
They are reused on every run — never downloaded again.

---

## Step 7 — Run the Server

**Option A — One-click (recommended):**

Double-click `run.bat` in the project folder.

**Option B — Manual via PowerShell:**
```powershell
venv\Scripts\python.exe web_server.py
```

**Expected terminal output:**
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

Open your browser and go to: **http://localhost:8080**

To stop the server: press `Ctrl + C` in the terminal.

---

## Step 8 — Use PolyVerba

1. **Select Input Language:**
   - `English Only (faster)` — use when speaker talks in English. Uses `base.en` model. Fastest.
   - `Auto-Detect` — use when speaker may speak in Hindi, Tamil, etc. Uses `small` model.

2. **Select Translate To:** Choose the target language from the dropdown (Hindi, Marathi, Tamil, etc.)

3. **Press Start**
   - First time: models load in ~12–15 seconds
   - After that: loads in ~2–3 seconds

4. **Play audio** from any application (YouTube, Zoom, etc.) — audio routes through VB-Cable automatically

5. **Captions appear** in ~3–4 seconds as grey words, then turn bright white when confirmed

6. **Switch language** at any time — a divider label appears and new language starts immediately

---

## Latency Reference

| Stage | Time |
|---|---|
| Model loading (first run) | ~12–15 seconds |
| Model loading (subsequent) | ~2–3 seconds |
| Audio → first grey words | ~3–4 seconds |
| Grey → confirmed white text | ~1–1.5 seconds |
| Steady-state end-to-end | ~1.5 seconds |

---

## Troubleshooting

**"Port 8080 already in use" or server won't start:**
```powershell
netstat -ano | findstr :8080
# Note the PID number shown, then:
taskkill /PID <number> /F
# Then start again
```

**"Listening..." but no captions appear:**
- Make sure VB-Cable is set as default playback device
- Make sure audio is actually playing in another app
- Check the terminal — look for `[STT ERROR]` or `[TRANSLATION ERROR]` lines
- Restart the server

**VB-Audio not detected:**
- Open `mmsys.cpl` → ensure `CABLE Input` is set as default Playback device
- Restart Windows Audio service: `Win + R` → `services.msc` → find `Windows Audio` → right-click → Restart

**Volume keys not working after VB-Cable setup:**
VB-Cable redirects audio away from physical speakers. To fix:
- Go to `mmsys.cpl` → Playback tab → enable "Listen to this device" on CABLE Output (as shown in Step 2)
- This routes VB-Cable audio back to your physical speakers with volume control

**Hindi works but Kannada text looks wrong (appears in Hindi script):**
This is a known limitation of the `dist-200M` model. Kannada, Tamil, Telugu, Gujarati output is phonetically correct but shown in Devanagari script. The `1B` model (planned for cloud deployment) fixes this.

**`venv\Scripts\activate` gives execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try again.

---

## File Structure Reference

```
POLYVERBA - self/
├── web_server.py          ← Run this to start the server
├── run.bat                ← Double-click launcher (runs web_server.py)
├── requirements.txt       ← All Python dependencies
├── stt/
│   ├── whisper_engine.py  ← Whisper STT wrapper
│   ├── system_audio.py    ← Audio capture pipeline
│   └── translate.py       ← Language code mapping
├── translation/
│   └── indictrans_engine.py  ← IndicTrans2 translation
└── web/
    ├── templates/
    │   └── index.html     ← Main UI page
    └── static/
        ├── style.css      ← All styling
        └── app.js         ← Browser WebSocket client
```

The `web/` folder is the frontend — it needs no build step and is served automatically.

---

## Supported Languages

| Language | Script | Edge (dist-200M) |
|---|---|---|
| Hindi | Devanagari | ✅ Full support |
| Marathi | Devanagari | ✅ Full support |
| Bengali | Bengali | ✅ Full support |
| Urdu | Arabic/Nastaliq | ✅ Full support |
| Punjabi | Gurmukhi | ✅ Full support |
| Assamese | Bengali | ✅ Full support |
| Nepali | Devanagari | ✅ Full support |
| Kannada | Kannada | ⚠️ Content correct, Devanagari script |
| Tamil | Tamil | ⚠️ Content correct, Devanagari script |
| Telugu | Telugu | ⚠️ Content correct, Devanagari script |
| Gujarati | Gujarati | ⚠️ Content correct, Devanagari script |
| Malayalam | Malayalam | ⚠️ Content correct, Devanagari script |
| English | Latin | ✅ No translation (pass-through) |
