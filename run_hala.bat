@echo off
cd /d "%~dp0"
title Hala

rem --- find a compatible Python (3.11 - 3.13). Python 3.14+ has no PyAudio wheel yet.
set PY=
for %%V in (3.13 3.12 3.11) do (
  if not defined PY (
    py -%%V --version >nul 2>&1 && set PY=py -%%V
  )
)

if not defined PY (
  echo No compatible Python found. Hala needs Python 3.12 or 3.13.
  echo Opening the download page. Install it, tick "Add Python to PATH", then run this file again.
  start https://www.python.org/downloads/release/python-31210/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating environment with %PY% ...
  %PY% -m venv .venv
  if errorlevel 1 ( echo Failed to create the environment. & pause & exit /b 1 )
)

if not exist ".installed" (
  echo Installing requirements, first run only...
  ".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
  if errorlevel 1 (
    echo Install failed. Send the error text above to get help.
    pause
    exit /b 1
  )
  echo ok> .installed
)

if "%ANTHROPIC_API_KEY%"=="" (
  set /p ANTHROPIC_API_KEY=Paste your Anthropic API key and press Enter:
  setx ANTHROPIC_API_KEY "%ANTHROPIC_API_KEY%" >nul
)

echo Starting Hala... (Ctrl+Alt+Space to ask, or say "Hala")
".venv\Scripts\python.exe" hala_main.py
pause
