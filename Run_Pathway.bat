@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python was not found. Install Python 3.10 or newer from python.org and select "Add Python to PATH".
    pause
    exit /b 1
  )
  set "PY=python"
)
echo Installing or checking app packages...
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)
echo Starting Pathway. Keep this window open while using the app.
%PY% -m streamlit run app.py
if errorlevel 1 pause
