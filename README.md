# 🐔 Stardew Valley Cross-Save Tool

A cross-platform GUI tool to sync your Stardew Valley save files across multiple devices using cloud storage (iCloud, OneDrive, Dropbox, etc.).

![Stardew Valley](assets/logo.png)

## 📋 Features

- **Cross-Platform Support**: Works on macOS, Windows, and Linux
- **Cloud Sync**: Automatically sync saves using your preferred cloud storage
- **Automatic Backups**: Creates backup copies before any operation
- **Symlink/Junction Management**: Uses native OS linking (symlinks on macOS/Linux, junctions on Windows)
- **User-Friendly GUI**: Themed interface with Stardew Valley colors and graphics
- **Safe Operations**: Migrates existing saves to cloud before creating links

## 🎮 How It Works

The tool creates a symbolic link (or junction on Windows) from your local Stardew Valley saves folder to a folder inside your cloud storage. This way:

1. Stardew Valley continues to read/write saves from its original location
2. The saves are actually stored in your cloud folder
3. Cloud storage automatically syncs saves across all your devices
4. You can play on different computers and continue where you left off

## 💻 System Requirements

- **Python 3.x** (3.8 or higher recommended)
- **Operating System**: macOS, Windows, or Linux
- **Cloud Storage**: iCloud, OneDrive, Dropbox, Google Drive, or any synced folder

### Python Dependencies

- `tkinter` (usually included with Python)
- `Pillow` (for image handling)

## 🚀 Installation

### Option 1: Download Pre-Built Application

**macOS:**
1. Download `Stardew Valley Cross-Save Tool.pkg` from [Releases](../../releases)
2. Double-click to install
3. Find the app in your Applications folder

**Windows:**
1. Download `Stardew Valley Cross-Save Tool.exe` from [Releases](../../releases)
2. Run the executable
3. No installation required

### Option 2: Run from Source

```bash
# Clone the repository
git clone <repository-url>
cd "Symlinking Tool"

# Install dependencies
pip3 install pillow

# Run the application
python3 app.py
```

## 📖 Usage

### First Time Setup

1. **Launch the application**
   
2. **Select Game Saves Folder**
   - Click "Choose…" next to "Game Saves Folder"
   - Navigate to your Stardew Valley saves location:
     - **macOS**: `~/Library/Application Support/StardewValley/Saves` or `~/.config/StardewValley/Saves`
     - **Windows**: `%AppData%\StardewValley\Saves`
     - **Linux**: `~/.config/StardewValley/Saves`

3. **Select Cloud Folder**
   - Click "Choose…" next to "Cloud Folder"
   - Select your cloud storage folder (e.g., `~/iCloud`, `~/OneDrive`, `~/Dropbox`)

4. **Create the Link**
   - Click "2️⃣ Link Saves → Cloud"
   - The tool will:
     - Create a backup of your current saves
     - Copy saves to the cloud folder
     - Create a symlink/junction from the game folder to the cloud

5. **Done!** Your saves are now synced via cloud storage

### Operations

- **1️⃣ Migrate to Cloud**: Copy local saves to cloud (without creating link)
- **2️⃣ Link Saves → Cloud**: Full setup - backup, migrate, and create symlink
- **♻️ Restore Backup**: Restore the last backup and remove the link

### Important Notes

⚠️ **Always backup your saves manually before using this tool**

- The tool creates automatic backups in `~/StardewValleyCrossSaves_Backups`
- Only one backup is kept in memory (the most recent one)
- Older backups must be restored manually if needed

## 🛠️ Building from Source

### macOS

```bash
# Make the script executable
chmod +x build_macos.sh

# Run the build script
./build_macos.sh
```

This creates:
- `dist/Stardew Valley Cross-Save Tool.app` (application bundle)
- `Stardew Valley Cross-Save Tool.pkg` (installer package)

### Windows

```bat
# Run the build script
build_windows.bat
```

This creates:
- `dist/Stardew Valley Cross-Save Tool/Stardew Valley Cross-Save Tool.exe`

For a professional installer, use [Inno Setup](https://jrsoftware.org/isinfo.php)

### Linux

```bash
# Install dependencies
pip3 install pillow pyinstaller

# Build
pyinstaller --windowed \
            --name "Stardew Valley Cross Saves Tool" \
            --add-data "assets:assets" \
            app.py
```

## 📁 Project Structure

```
Symlinking Tool/
├── app.py                      # Main application
├── build_macos.sh              # macOS build script
├── build_windows.bat           # Windows build script
├── assets/
│   ├── logo.png                # Application logo (PNG)
│   ├── logo.icns               # macOS icon
│   ├── logo.ico                # Windows icon
│   └── background.jpg          # UI background image
├── test/                       # Test folders
│   ├── Cloud/Saves/
│   └── Original/Saves/
├── .github/
│   └── copilot-instructions.md # AI/Copilot guidelines
├── .gitignore
└── README.md
```

## 🎨 Technology Stack

- **Language**: Python 3.x
- **GUI Framework**: Tkinter
- **Image Processing**: Pillow (PIL)
- **Build Tool**: PyInstaller
- **Platform Detection**: Platform-specific symlink/junction handling

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is not affiliated with or endorsed by ConcernedApe or Stardew Valley. Use at your own risk. Always maintain backups of your save files.

## 🐛 Troubleshooting

### "The game Saves folder appears to already be a link/junction"

This means a link already exists. Use "♻️ Restore Backup" first to remove it, then try again.

### Saves not syncing

1. Verify your cloud storage is actively syncing
2. Check that the cloud folder path is correct
3. Ensure you have write permissions to both folders

### Permission denied on macOS

macOS may require explicit permissions. Grant Full Disk Access:
1. System Preferences → Security & Privacy → Privacy
2. Select "Full Disk Access"
3. Add Python or the Terminal app

## 💬 Support

For issues, questions, or suggestions:
- Open an [Issue](../../issues)
- Check existing issues for solutions

---

Made with ❤️ for the Stardew Valley community
