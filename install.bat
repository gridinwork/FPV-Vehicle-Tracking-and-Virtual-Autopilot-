@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Python launcher "py" was not found. Install Python 3.10+ from python.org.
  pause
  exit /b 1
)

py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto fail
)

set "PY=%~dp0.venv\Scripts\python.exe"
echo Using %PY%
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto fail

nvidia-smi >nul 2>&1
if errorlevel 1 goto cpu

echo NVIDIA GPU detected. Installing a CUDA build of PyTorch.
"%PY%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
if not errorlevel 1 goto deps
echo cu128 wheel failed, trying cu126.
"%PY%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
if not errorlevel 1 goto deps
echo cu126 wheel failed, trying cu124.
"%PY%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
if not errorlevel 1 goto deps
echo CUDA wheels failed. Falling back to the default PyTorch build.

:cpu
echo Installing the default PyTorch build.
"%PY%" -m pip install torch torchvision
if errorlevel 1 goto fail

:deps
echo Installing application dependencies.
"%PY%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto fail

"%PY%" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 2)"
if errorlevel 2 (
  echo PyTorch lost CUDA after dependency install. Restoring the CUDA wheel.
  "%PY%" -m pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu128
)

echo Running detector, tracker, and video self-check...
"%PY%" "%~dp0tools\self_check.py"
if errorlevel 1 goto fail

echo.
echo Installation complete. Start the application with start.bat
pause
exit /b 0

:fail
echo.
echo Installation failed.
pause
exit /b 1
