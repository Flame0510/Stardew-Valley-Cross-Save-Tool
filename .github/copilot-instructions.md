# GitHub Copilot Instructions - Stardew Valley Cross-Save Tool

## Project Overview

This is a cross-platform GUI application for syncing Stardew Valley save files across devices using cloud storage (iCloud, OneDrive, Dropbox, etc.). The tool creates symbolic links (macOS/Linux) or junctions (Windows) from the game's saves folder to a cloud-synced folder.

**Key Updates (December 2025):**
- Removed game version detection (too unreliable across platforms)
- Kept game installation detection with warning if not found
- Added version compatibility warning banner for PC/Mobile sync
- Implemented GitHub Actions for automated multi-platform builds
- Enhanced build scripts with permission management

## Technology Stack

- **Language**: Python 3.x
- **GUI**: Tkinter (native, no external dependencies for GUI)
- **Image Processing**: Pillow (PIL) for logo and background
- **Build**: PyInstaller for creating standalone executables
- **Platform Support**: macOS, Windows, Linux

## Code Architecture

### Main File: `app.py`

- **Entry Point**: `main()` function
- **Main Class**: `App(tk.Tk)` - GUI application class
- **Platform Detection**: `is_windows()`, `is_macos()` helper functions
- **File Operations**: 
  - `create_symlink_dir()` for macOS/Linux
  - `create_junction_windows()` for Windows
  - `backup_folder()`, `copy_contents()`, `remove_path()`

### Key Operations

1. **Migrate to Cloud**: Copy saves to cloud without creating link
2. **Link Game to Cloud**: 
   - Backup existing saves
   - Copy saves to cloud folder
   - Remove original folder
   - Create symlink/junction pointing to cloud
3. **Restore Backup**: Remove link and restore from backup
4. **Auto-Detection**:
   - `find_game_installation()` - Detects game installation (no version)
   - `find_game_saves_path()` - Auto-finds saves folder
   - Shows warning popup if game not found

## Design System

### Colors (Stardew Valley Theme)

```python
COLORS = {
    'bg': '#8B4513',           # Brown (wood)
    'bg_dark': '#5D2E0F',      # Dark brown
    'bg_light': '#D2B48C',     # Light tan
    'primary': '#5C8A3D',      # Stardew green
    'primary_dark': '#3D5A29', # Dark green
    'accent': '#F4A460',       # Sandy brown
    'text': '#3E2723',         # Dark brown text
    'text_light': '#FFFFFF',   # White text
    'button': '#8FBC8F',       # Light green
    'button_hover': '#6B9B6B', # Darker green
    'button_text': '#2C1810',  # Very dark brown
    'error': '#C74440',        # Red
    'success': '#5C8A3D',      # Green
}
```

### Fonts

- **Title**: Georgia, 20pt, bold
- **Subtitle**: Georgia, 13pt
- **Labels**: Georgia, 16pt, bold
- **Hints**: Georgia, 12pt, italic
- **Buttons**: Georgia, 13pt, bold
- **Entries**: Courier, 11pt
- **Log**: Courier, 10pt

### UI Standards

- **Border Widths**: 
  - Entries: 1px (`bd=1`)
  - Buttons/Frames: 2px (`bd=2`)
- **Layout**: Responsive with `relwidth`/`relheight`
- **Window**: 1000x800 default, 900x700 minimum
- **Background**: Dynamic resizing on window resize (debounced)

## Important Constants

```python
APP_TITLE = "Stardew Valley Cross Saves Tool"  # Single source of truth
```

**Always use `APP_TITLE` constant** instead of hardcoding the application name.

## Critical Code Patterns

### ⚠️ IMPORTANT: Order of Operations in link_game_to_cloud()

```python
# CORRECT ORDER (current implementation):
1. Ensure cloud folder exists
2. Copy saves to cloud (copy_contents())  # MUST be BEFORE removing local
3. Backup local saves
4. Remove original saves folder
5. Create symlink/junction

# WRONG (will lose data):
# DO NOT remove local folder before copying to cloud!
```

### Platform-Specific Linking

```python
if is_windows():
    create_junction_windows(link_path, target_path)  # mklink /J
else:
    create_symlink_dir(link_path, target_path)       # os.symlink
```

### Path Handling

- Always use `Path` from `pathlib`
- Normalize with `norm()` function
- Check existence with `path_exists()`
- Detect links with `is_link()` or `is_junction_windows()`

## Assets

- `assets/logo.png` - 60x60px logo for UI
- `assets/logo.icns` - macOS application icon
- `assets/logo.ico` - Windows application icon
- `assets/background.jpg` - UI background (dynamically resized)

## Build Scripts

### macOS: `build_macos.sh`

- Creates `.app` bundle with PyInstaller
- Packages as `.pkg` installer with `pkgbuild`
- Uses `assets/logo.icns` for app icon
- **Permission Fixes**: Uses `find` with `chmod` to recursively fix permissions before cleanup
- Error suppression: `2>/dev/null || true` for clean builds

### Windows: `build_windows.bat`

- Creates standalone `.exe` with PyInstaller
- Uses `assets\logo.ico` for app icon
- **Permission Fixes**: Uses `attrib -r -h` to remove read-only/hidden flags before cleanup
- Error suppression: `2>nul` on all removal commands
- Suggests Inno Setup for professional installer

### Linux: `build_linux.sh`

- Creates single-file executable with PyInstaller `--onefile`
- **Permission Fixes**: Same pattern as macOS (find + chmod)
- Includes AppImage creation instructions
- Error suppression for clean builds

## GitHub Actions

**File**: `.github/workflows/build.yml`

**Trigger**: 
- Push to tags matching `v*`
- Manual workflow dispatch
- Release creation

**Jobs**:
1. **build-windows**: Windows executable (runs-on: windows-latest)
2. **build-macos**: macOS .app and .pkg (runs-on: macos-latest)
3. **build-linux**: Linux standalone executable (runs-on: ubuntu-latest)
4. **create-release**: Creates GitHub Release with ZIP artifacts (runs-on: ubuntu-latest)

**Permissions**: `contents: write` (workflow and job level)

**Release Action**: `ncipollo/release-action@v1` with `allowUpdates: true`

**Artifacts**: ZIP archives uploaded to GitHub Releases:
- `StardewCrossSave-Windows.zip`
- `StardewCrossSave-macOS.zip`
- `StardewCrossSave-Linux.zip`

## Coding Conventions

### Style

- **Language**: English (code, comments, UI)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Not required for simple functions, use for complex logic
- **Type Hints**: Used for return types on utility functions

### Error Handling

```python
try:
    # Operation
except Exception as e:
    messagebox.showerror(APP_TITLE, str(e))
    self._log(f"[ERROR] {e}")
```

### Logging Pattern

```python
self._log("[OPERATION] Description")
self._log("[OK] Success message")
self._log("[ERROR] Error details")
self._log("[INFO] Information")
```

## Common Tasks

### Adding a New Button

1. Add to `buttons_data` list in `_build()` method
2. Follow pattern: `(emoji + text, callback, bg_color, fg_color)`
3. Use `COLORS` dict for consistent styling
4. Implement callback method in `App` class

### Modifying UI Elements

- Always use `COLORS` dict for colors
- Maintain border width standards (1px entries, 2px buttons)
- Use Georgia font for text, Courier for code/paths
- Ensure responsive layout with `relwidth`/`relheight`

### Working with Paths

```python
# Good:
path = Path(user_input).expanduser().resolve()
normalized = norm(str(path))

# Bad:
path = user_input  # Don't use raw strings
```

### Platform Detection

```python
if is_windows():
    # Windows-specific code
elif is_macos():
    # macOS-specific code
else:
    # Linux-specific code
```

## Testing

Test directories are included in `test/`:
- `test/Original/Saves` - Mock game saves folder
- `test/Cloud/Saves` - Mock cloud folder

## Git Workflow

### Commit Message Convention

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build scripts, dependencies, etc.

### Ignored Files

See `.gitignore`:
- Build artifacts: `build/`, `dist/`, `*.spec`, `*.pkg`
- Python cache: `__pycache__/`, `*.pyc`

## Known Issues & Quirks

1. **Background Resize**: Debounced to avoid excessive reloads (50px threshold, 100ms delay)
2. **Junction Detection**: Windows junctions need special handling with `fsutil`
3. **Backup Limitation**: Only one backup kept in `self.backup_path` (in memory)
4. **macOS Permissions**: May require Full Disk Access for Library folder access
5. **Version Detection Removed**: Game version detection removed (too unreliable). Users must manually verify PC/Mobile compatibility
6. **Installation Detection**: Still detects game installation but doesn't extract version number

## Development Guidelines

### When Adding Features

1. Maintain backward compatibility with existing save structures
2. Always create backups before destructive operations
3. Log all operations to the status log
4. Show user-friendly error messages via messagebox
5. Test on both Windows and macOS if possible

### When Fixing Bugs

1. Check if it affects platform-specific code (symlinks vs junctions)
2. Ensure the fix doesn't break the operation order in `link_game_to_cloud()`
3. Update logs to help with debugging
4. Consider edge cases (empty folders, permissions, existing links)

### When Refactoring

1. Use `APP_TITLE` constant for application name
2. Extract colors to `COLORS` dict
3. Keep consistent border widths and fonts
4. Don't change the core operation logic without thorough testing

## Resources

- **Stardew Valley Save Location**: https://stardewvalleywiki.com/Saves
- **PyInstaller Documentation**: https://pyinstaller.org/
- **Tkinter Reference**: https://docs.python.org/3/library/tkinter.html
- **Pillow Documentation**: https://pillow.readthedocs.io/

## Questions to Ask

When working on this project, consider:

1. **Does this change affect both Windows and macOS?**
2. **Will this preserve user data if something goes wrong?**
3. **Is the error message clear and actionable?**
4. **Does this follow the Stardew Valley color scheme?**
5. **Is the operation logged for debugging?**
6. **Have I used the `APP_TITLE` constant instead of hardcoding?**

## DRY Principles Applied

- Single `APP_TITLE` constant used throughout
- `COLORS` dict for all color values
- Reusable utility functions (`norm()`, `ensure_dir()`, etc.)
- Consistent border widths and fonts

---

**Remember**: This tool handles user save data. Safety and data integrity are the top priorities. Always backup, always log, always handle errors gracefully.
