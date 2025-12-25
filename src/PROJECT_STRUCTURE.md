# Project Structure

This project uses a modular architecture following SOLID principles and Design Patterns.

## Directory Structure

```
Stardew Valley Cross-Save Tool/
├── main.py                     # Main entry point
├── app.py                      # Legacy entry point (backward compatibility)
├── src/                        # Source code modules
│   ├── __init__.py
│   ├── config.py              # Singleton: Configuration management
│   ├── strategies/            # Strategy Pattern: Platform-specific operations
│   │   ├── __init__.py
│   │   ├── link_strategy.py   # LinkStrategy, SymlinkStrategy, JunctionStrategy
│   │   └── platform_factory.py # Factory for creating strategies
│   ├── detection/             # Detection services
│   │   ├── __init__.py
│   │   ├── path_detector.py   # PathDetector implementations (macOS/Windows/Linux)
│   │   └── game_detection.py  # GameDetectionService
│   ├── operations/            # Command Pattern: Operations
│   │   ├── __init__.py
│   │   ├── file_operations.py # Facade: File system operations
│   │   └── commands.py        # MigrateCommand, LinkCommand, RestoreCommand
│   └── ui/                    # User Interface
│       ├── __init__.py
│       ├── widget_factory.py  # Factory: UI widget creation
│       └── main_window.py     # Main application window
├── assets/                    # Images and resources
│   ├── logo.png
│   ├── logo.icns
│   ├── logo.ico
│   └── background.jpg
├── test/                      # Test data
├── build_macos.sh
├── build_windows.bat
├── build_linux.sh
├── README.md
└── ARCHITECTURE.md

```

## Module Responsibilities

### `src/config.py`
- **Pattern**: Singleton
- **Responsibility**: Centralized configuration (colors, fonts, paths)
- **Dependencies**: None

### `src/strategies/`
- **Pattern**: Strategy, Factory
- **Responsibility**: Platform-specific link operations (symlinks vs junctions)
- **Key Classes**:
  - `LinkStrategy` (ABC)
  - `SymlinkStrategy` (macOS/Linux)
  - `JunctionStrategy` (Windows)
  - `PlatformFactory`

### `src/detection/`
- **Pattern**: Strategy, Factory
- **Responsibility**: Detect game installation and save paths
- **Key Classes**:
  - `PathDetector` (ABC)
  - `MacOSPathDetector`, `WindowsPathDetector`, `LinuxPathDetector`
  - `PathDetectorFactory`
  - `GameDetectionService`

### `src/operations/`
- **Pattern**: Command, Facade
- **Responsibility**: File operations and undoable commands
- **Key Classes**:
  - `FileOperations` (Facade for file system)
  - `Command` (ABC)
  - `MigrateCommand`, `LinkCommand`, `RestoreCommand`
  - `OperationResult` (Value Object)

### `src/ui/`
- **Pattern**: Factory, Template Method
- **Responsibility**: User interface components
- **Key Classes**:
  - `WidgetFactory` (creates styled widgets)
  - `StardewCrossSaveApp` (main window)

## Running the Application

### From Source
```bash
# New way (recommended)
python3 main.py

# Old way (backward compatible)
python3 app.py
```

### Building Executables
```bash
# macOS
./build_macos.sh

# Windows
build_windows.bat

# Linux
./build_linux.sh
```

## Benefits of Modular Structure

1. **Single Responsibility**: Each module has one focused purpose
2. **Easy Testing**: Modules can be tested independently
3. **Better Organization**: Related code grouped together
4. **Reduced File Size**: Main files are ~100-300 lines instead of 1100+
5. **Easier Maintenance**: Changes localized to specific modules
6. **Clear Dependencies**: Import structure shows relationships
7. **Reusability**: Modules can be reused in other projects

## Import Examples

```python
# Import configuration
from src.config import Config

# Import strategies
from src.strategies import LinkStrategy, PlatformFactory

# Import detection
from src.detection import PathDetectorFactory, GameDetectionService

# Import operations
from src.operations import FileOperations, MigrateCommand, LinkCommand

# Import UI
from src.ui import WidgetFactory, StardewCrossSaveApp
```

## Migration from Old Structure

The old monolithic `app.py` (1100+ lines) has been split into focused modules:

- **Lines 1-80**: → `src/config.py` (50 lines)
- **Lines 81-160**: → `src/strategies/link_strategy.py` (70 lines)
- **Lines 161-250**: → `src/detection/path_detector.py` (90 lines)
- **Lines 251-370**: → `src/detection/game_detection.py` (60 lines)
- **Lines 371-540**: → `src/operations/` (180 lines split across 2 files)
- **Lines 541-664**: → `src/ui/widget_factory.py` (130 lines)
- **Lines 665-1078**: → `src/ui/main_window.py` (350 lines)

**Result**: 
- Old: 1 file × 1100 lines = 1100 lines
- New: 12 files × ~100-350 lines each = ~1000 lines (with better organization!)

## Design Patterns Used

1. **Singleton**: `Config` class
2. **Strategy**: `LinkStrategy` hierarchy
3. **Factory**: `PlatformFactory`, `PathDetectorFactory`, `WidgetFactory`
4. **Command**: `MigrateCommand`, `LinkCommand`, `RestoreCommand`
5. **Facade**: `FileOperations`
6. **Template Method**: `StardewCrossSaveApp._build_ui()`

For detailed architecture documentation, see [ARCHITECTURE.md](../ARCHITECTURE.md).
