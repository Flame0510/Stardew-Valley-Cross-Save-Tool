#!/bin/bash
# Build script for Linux
# Generates AppImage-ready application

set -e  # Exit on error

echo "=========================================="
echo "  Stardew Valley Cross-Save Tool - Build Linux"
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
if [ -d "dist" ]; then
    find dist -type d -exec chmod 755 {} \; 2>/dev/null || true
    find dist -type f -exec chmod 644 {} \; 2>/dev/null || true
fi
rm -rf build dist "Stardew Valley Cross-Save Tool.spec" 2>/dev/null || true

# Build application
echo ""
echo "🔨 Building application..."
pyinstaller --onefile \
            --windowed \
            --name "Stardew Valley Cross-Save Tool" \
            --add-data "assets:assets" \
            app.py --noconfirm

echo ""
echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
echo ""
echo "Generated file:"
echo "  - dist/Stardew Valley Cross-Save Tool  (executable)"
echo ""
echo "To run: ./dist/Stardew\ Valley\ Cross-Save\ Tool"
echo ""
echo "Optional: Create AppImage for distribution:"
echo "  - Download appimagetool from https://appimage.github.io/"
echo "  - Package with: appimagetool dist/ StardewCrossSave.AppImage"
echo ""
