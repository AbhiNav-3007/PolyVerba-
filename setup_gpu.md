# PolyVerba - GPU Setup & Sharing Guide

This guide details how to correctly share your local PolyVerba project with a friend who has a dedicated NVIDIA GPU, and how they should set it up so that it utilizes their GPU for maximum speed (sub-0.5s latency).

---

## PART 1: How to Share the Project (For You)

Do not just copy the entire folder directly to a pen drive. Python environments and locally downloaded ML models are massive and PC-specific. 

1. **Clean the project folder:**
   - **DO NOT** send the `venv` folder (it contains your computer's specific Python files, ~2.5GB).
   - **DO NOT** send the HuggingFace cache folder if it exists inside the project (`.cache` or similar, ~1.5GB).
2. **Zip the folder:**
   - Right-click the `POLYVERBA - self` folder → **Compress to ZIP file**.
   - The resulting ZIP should be very small (just your Python scripts, UI files, and markdown docs).
3. **Share:**
   - Send this ZIP file via Google Drive, Telegram, or a USB drive.

---

## PART 2: How to Setup on the GPU Laptop (For Your Friend)

### Step 1 — Install System Prerequisites
Before doing anything with Python, your friend must install these system tools:

**1. Python 3.10**
- Download Python 3.10.x (must be exactly 3.10 to avoid dependency conflicts).
- **CRITICAL:** Check the box "Add Python 3.10 to PATH" during installation.

**2. FFmpeg**
- Download FFmpeg, extract it, and add the `bin` folder to Windows Environment Variables (`PATH`).

**3. Git for Windows**
- Download and install Git (required for HuggingFace to authenticate properly).

### Step 2 — Configure Audio Routing (VB-Cable)
This step is mandatory. PolyVerba needs a "digital wire" to capture system audio.

1. Go to [vb-audio.com/Cable](https://vb-audio.com/Cable/) and download VB-Cable.
2. Extract the ZIP, right-click `VBCABLE_Setup_x64.exe` and select **Run as Administrator**. Restart PC if prompted.
3. **Set the Default Output:**
   - Press `Win + I` → System → Sound.
   - Set **Choose where to play sound (Output)** to normal Speakers or Earbuds.
4. **Route the Browser:**
   - Open Chrome or Brave and play a YouTube video.
   - Go to System → Sound → **Volume mixer**.
   - Find the browser in the list and change its **Output device** to `CABLE Input (VB-Audio Virtual Cable)`.
5. **Listen to the Cable:**
   - Press `Win + R`, type `mmsys.cpl` and press Enter.
   - Go to the **Recording** tab.
   - Right-click `CABLE Output` → **Properties** → **Listen** tab.
   - Check the box **"Listen to this device"**.
   - Set the dropdown below it to **"Default Playback Device"**.
   - Click Apply and OK.

### Step 3 — Extract the Project
1. Extract the ZIP file you sent them into a folder (e.g., `Documents\PolyVerba`).
2. Open PowerShell or Command Prompt and `cd` into that folder.

### Step 4 — Ensure GPU is Recognized
1. In the terminal, type:
   ```powershell
   nvidia-smi
   ```
2. Look at the top right of the output table. It will say `CUDA Version: 11.8` or `12.1` or `12.x`. 
   - *Note down this CUDA version.*

### Step 5 — Create Virtual Environment
Create a fresh environment specific to this laptop:
```powershell
py -3.10 -m venv venv
venv\Scripts\activate
```
*(If you get a security error running activate, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### Step 6 — Install GPU-Specific PyTorch (CRITICAL STEP)
This is the only difference from the CPU setup. We must install the version of PyTorch that talks to the GPU.

**If their CUDA version is 11.8:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**If their CUDA version is 12.1 or higher:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Step 7 — Install Remaining Dependencies
Now install the rest of the required packages:
```powershell
# Core ML dependencies
pip install transformers==4.37.2 sentencepiece sacremoses indic-nlp-library accelerate

# Audio Processing
pip install faster-whisper soundcard sounddevice numpy scipy ffmpeg-python

# Server
pip install fastapi uvicorn jinja2 websockets python-multipart psutil
```

### Step 8 — HuggingFace Login
Just like on your machine, your friend needs to authenticate to download IndicTrans2.
1. Run:
   ```powershell
   huggingface-cli login
   ```
2. Paste a HuggingFace Read token (You can provide yours, or they can generate their own on huggingface.co).

### Step 9 — Run the Application
```powershell
python web_server.py
```
- Open `http://localhost:8080` in Chrome/Brave.
- The UI and architecture will be **exactly the same**. They can choose "English Only" (`base.en`) or "Auto-Detect" (`small`). 
- Because they installed the CUDA version of PyTorch, once we update the code (in Phase 9) to say `device="cuda"`, the models will load directly into the GPU's VRAM.

### How to Verify It's Running on GPU?
1. Open Task Manager (`Ctrl + Shift + Esc`).
2. Go to the **Performance** tab and click on **GPU**.
3. When they press **Start** on the PolyVerba UI and play a YouTube video, the **Dedicated GPU Memory** usage will spike (by ~500MB+ for the models), and the **Compute / 3D** graph will show activity. 
4. The latency will be aggressively fast (~0.3 seconds).
