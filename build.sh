#!/bin/bash
# =============================================
# OtoServis Pro — Linux Build Script
# =============================================
#
# Prerequisites:
#   1. Python 3.10+ installed
#   2. Virtual environment activated: source venv/bin/activate
#   3. pip install -r requirements.txt
#
# Usage:
#   chmod +x build.sh
#   ./build.sh
# =============================================

echo ""
echo "========================================"
echo "  OtoServis Pro — Build Başlatılıyor"
echo "========================================"
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "HATA: Virtual environment aktif değil!"
    echo "Önce çalıştırın: source venv/bin/activate"
    exit 1
fi

# Install build dependencies
echo "[1/3] Gerekli paketler yükleniyor..."
pip install pyinstaller pywebview --quiet

# Run PyInstaller
echo "[2/3] PyInstaller ile uygulama oluşturuluyor..."
pyinstaller otoservis.spec --noconfirm

# Copy extra files to dist
echo "[3/3] Dağıtım dosyaları kopyalanıyor..."
mkdir -p dist
cp -f README.txt dist/ 2>/dev/null
cp -f config.ini dist/ 2>/dev/null

echo ""
echo "========================================"
echo "  Build tamamlandı!"
echo "  Çıktı: dist/OtoServis"
echo "========================================"
echo ""
