@echo off
REM =============================================
REM OtoServis Pro — Windows Build Script
REM =============================================
REM
REM Prerequisites:
REM   1. Python 3.10+ installed
REM   2. pip install -r requirements.txt
REM   3. pip install pyinstaller pywebview
REM
REM Usage:
REM   build.bat
REM =============================================

echo.
echo ========================================
echo   OtoServis Pro — Build Baslatiliyor
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install build dependencies
echo [1/3] Gerekli paketler yukleniyor...
pip install pyinstaller pywebview --quiet

REM Run PyInstaller
echo [2/3] PyInstaller ile exe olusturuluyor...
pyinstaller otoservis.spec --noconfirm

REM Copy extra files to dist
echo [3/3] Dagitim dosyalari kopyalaniyor...
if not exist dist mkdir dist
copy /Y README.txt dist\ >nul 2>&1
copy /Y config.ini dist\ >nul 2>&1

echo.
echo ========================================
echo   Build tamamlandi!
echo   Cikti: dist\OtoServis.exe
echo ========================================
echo.

pause
