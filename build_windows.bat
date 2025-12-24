@echo off
REM Build script for Windows
REM Generates .exe application

echo ==========================================
echo   Stardew Cross Saves Linker - Build Windows
echo ==========================================
echo.

REM Check Python 3
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found. Install Python 3 before continuing.
    echo     Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Install dependencies
echo.
echo [*] Installing dependencies...
python -m pip install pillow pyinstaller --upgrade --quiet

REM Clean previous builds
echo.
echo [*] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Stardew Cross Saves Linker.spec" del "Stardew Cross Saves Linker.spec"

REM Build application
echo.
echo [*] Building application...
pyinstaller --windowed --name "Stardew Cross Saves Linker" --add-data "assets;assets" --icon "assets\logo.png" symlinking.py --noconfirm

echo.
echo ==========================================
echo [OK] Build completed successfully!
echo ==========================================
echo.
echo Generated file:
echo   - dist\Stardew Cross Saves Linker\Stardew Cross Saves Linker.exe
echo.
echo To create a professional installer (.exe), use Inno Setup:
echo   https://jrsoftware.org/isinfo.php
echo.
pause
