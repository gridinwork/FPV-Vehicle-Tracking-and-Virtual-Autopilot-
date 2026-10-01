@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "%~dp0main.py"
if errorlevel 1 (
  echo.
  echo The application exited with an error. The traceback is above.
  echo Details are also in logs\app.log
  pause
  exit /b 1
)
