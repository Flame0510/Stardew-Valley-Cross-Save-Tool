#!/bin/bash
# Build script for macOS
# Generates .app application and .pkg installer package

set -e  # Exit on error

echo "=========================================="
echo "  Stardew Cross Saves Linker - Build macOS"
echo "=========================================="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3 before continuing."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install pillow pyinstaller --quiet
echo "✓ Dependencies installed"

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf build dist "Stardew Cross Saves Linker.pkg" "Stardew Cross Saves Linker.spec"

# Build application
echo ""
echo "🔨 Building application..."
pyinstaller --windowed \
            --name "Stardew Cross Saves Linker" \
            --add-data "assets:assets" \
            --icon "assets/logo.png" \
            symlinking.py --noconfirm

# Create .pkg package
echo ""
echo "📦 Creating .pkg installer..."
pkgbuild --component "dist/Stardew Cross Saves Linker.app" \
         --install-location /Applications \
         "Stardew Cross Saves Linker.pkg"

echo ""
echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - dist/Stardew Cross Saves Linker.app  (application)"
echo "  - Stardew Cross Saves Linker.pkg        (installer)"
echo ""
echo "To install: double-click 'Stardew Cross Saves Linker.pkg'"
echo ""
