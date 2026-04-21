@echo off
echo Starting PolyVerba...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python web_server.py
pause
