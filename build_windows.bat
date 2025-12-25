@echo off
REM Build script for Windows
REM Generates .exe application

echo ==========================================
echo   Stardew Valley Cross-Save Tool - Build Windows
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
if exist build (
    attrib -r -h build\*.* /s /d >nul 2>&1
    rmdir /s /q build 2>nul
)
if exist dist (
    attrib -r -h dist\*.* /s /d >nul 2>&1
    rmdir /s /q dist 2>nul
)
if exist "Stardew Valley Cross-Save Tool.spec" del /f /q "Stardew Valley Cross-Save Tool.spec" 2>nul

REM Build application
echo.
echo [*] Building application...
pyinstaller --windowed --name "Stardew Valley Cross-Save Tool" --add-data "assets;assets" --icon "assets\logo.ico" app.py --noconfirm

echo.
echo ==========================================
echo [OK] Build completed successfully!
echo ==========================================
echo.
echo Generated file:
echo   - dist\Stardew Valley Cross-Save Tool\Stardew Valley Cross-Save Tool.exe
echo.
echo To create a professional installer (.exe), use Inno Setup:
echo   https://jrsoftware.org/isinfo.php
echo.
pause
