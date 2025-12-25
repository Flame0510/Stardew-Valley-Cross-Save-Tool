#!/bin/bash
# Build script for macOS
# Generates .app application and .pkg installer package

set -e  # Exit on error

echo "=========================================="
echo "  Stardew Valley Cross-Save Tool - Build macOS"
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
rm -rf build dist "Stardew Valley Cross-Save Tool.pkg" "Stardew Valley Cross-Save Tool.spec" 2>/dev/null || true

# Build application
echo ""
echo "🔨 Building application..."
pyinstaller --windowed \
            --name "Stardew Valley Cross-Save Tool" \
            --add-data "assets:assets" \
            --add-data "src:src" \
            --icon "assets/logo.icns" \
            main.py --noconfirm

# Create .pkg package
echo ""
echo "📦 Creating .pkg installer..."
pkgbuild --component "dist/Stardew Valley Cross-Save Tool.app" \
         --install-location /Applications \
         "Stardew Valley Cross-Save Tool.pkg"

echo ""
echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - dist/Stardew Valley Cross Saves Tool.app  (application)"
echo "  - Stardew Valley Cross Saves Tool.pkg        (installer)"
echo ""
echo "To install: double-click 'Stardew Valley Cross Saves Tool.pkg'"
echo ""
