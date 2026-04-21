"""
PolyVerba - Web Server (FastAPI)

Single-server architecture:
  - Serves the premium glassmorphism UI at http://localhost:8080
  - Handles Start/Stop/Language-switch via REST API
  - Streams live captions to all connected browsers via WebSocket
  - Background task reads the result_queue and broadcasts to clients

Usage:
  python web_server.py
  Open http://localhost:8080
"""

import os
import sys
import asyncio
import time
import warnings
from contextlib import asynccontextmanager

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import stt.system_audio as system_audio
from stt.translate import FLORES_CODES, LANGUAGE_NAMES

# Track all connected WebSocket clients
connected_clients = set()


async def broadcast_captions():
    """
    Background task: continuously reads from the result_queue
    and broadcasts messages to all connected WebSocket clients.
    """
    while True:
        try:
            while not system_audio.result_queue.empty():
                message = system_audio.result_queue.get_nowait()

                # Send to all connected clients
                to_remove = set()
                for client in list(connected_clients):
                    try:
                        await client.send_json(message)
                    except Exception:
                        to_remove.add(client)

                # Clean up dead connections
                connected_clients.difference_update(to_remove)

            await asyncio.sleep(0.05)  # 50ms poll interval
        except Exception as e:
            print(f"[BROADCAST ERROR] {e}")
            await asyncio.sleep(0.1)


@asynccontextmanager
async def lifespan(app):
    """Launch the caption broadcaster when the server starts."""
    task = asyncio.create_task(broadcast_captions())
    yield
    task.cancel()


# --- App Setup ---------------------------------------------------------------

app = FastAPI(title="PolyVerba", lifespan=lifespan)

# Serve static CSS/JS assets
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Jinja2 templates for the HTML UI
templates = Jinja2Templates(directory="web/templates")


# --- Pages -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Serve the main captioning interface."""
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "languages": LANGUAGE_NAMES,
            "v": int(time.time())
        }
    )


# --- REST API ----------------------------------------------------------------

@app.post("/api/start")
async def start_transcription(data: dict):
    """Start the audio capture and translation pipeline."""
    target_lang  = data.get("target_lang", "Hindi")
    capture_mode = data.get("capture_mode", "loopback")
    # Model is chosen by user: 'base.en' (English only, faster) or 'small' (auto-detect)
    model = data.get("model", "base.en")

    translate = (target_lang != "English")

    success = system_audio.start_transcription(
        source_lang="en",
        target_lang=target_lang,
        model=model,
        translate=translate,
        capture_mode=capture_mode
    )

    if success:
        return {"status": "started", "message": f"[{model}] -> {target_lang}"}
    else:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to start. Check terminal for details."}
        )


@app.post("/api/stop")
async def stop_transcription():
    """Stop the audio capture pipeline."""
    system_audio.stop_transcription()
    return {"status": "stopped"}


@app.post("/api/update-target")
async def update_target(data: dict):
    """Switch the target language mid-stream without restarting."""
    target_lang = data.get("target_lang", "Hindi")
    system_audio.update_target(target_lang)
    return {"status": "updated", "target": target_lang}


@app.get("/api/status")
async def get_status():
    """Check if the pipeline is currently active."""
    return {
        "running": system_audio.is_running(),
        "target": system_audio._current_target,
        "capture_mode": system_audio.get_capture_mode()
    }


# --- WebSocket ---------------------------------------------------------------

@app.websocket("/ws/captions")
async def websocket_endpoint(websocket: WebSocket):
    """Accept WebSocket connections from browser clients."""
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"[WS] Client connected. Active: {len(connected_clients)}")
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[WS] Client disconnected. Active: {len(connected_clients)}")


# --- Entry Point -------------------------------------------------------------

def _free_port(port=8080):
    """Kill any process already using the given port (prevents Errno 10048)."""
    import subprocess, signal
    try:
        result = subprocess.check_output(
            f'netstat -ano | findstr :{port}', shell=True, text=True
        )
        pids = set()
        for line in result.strip().splitlines():
            parts = line.split()
            if parts and parts[-1].isdigit():
                pids.add(int(parts[-1]))
        for pid in pids:
            try:
                subprocess.call(f'taskkill /PID {pid} /F', shell=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[STARTUP] Freed port {port} (killed PID {pid})")
            except Exception:
                pass
    except Exception:
        pass  # Port is already free


if __name__ == "__main__":
    _free_port(8080)   # Auto-kill any stale server on port 8080

    print()
    print("=" * 55)
    print("  PolyVerba - Edge Multilingual Captioning System")
    print("  -----------------------------------------------")
    print("  Open in browser:  http://localhost:8080")
    print("  Press Ctrl+C to stop the server")
    print("=" * 55)
    print()

    try:
        uvicorn.run(app, host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"\n[FATAL] Server failed to start: {e}")
        import traceback
        traceback.print_exc()

