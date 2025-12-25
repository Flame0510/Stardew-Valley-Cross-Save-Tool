#!/usr/bin/env python3
"""
Stardew Valley Cross-Save Tool
===============================
A cross-platform tool for syncing Stardew Valley saves via cloud storage.

Architecture:
- Strategy Pattern: Platform-specific operations (symlink vs junction)
- Factory Pattern: Consistent widget creation
- Command Pattern: Undoable operations
- Singleton Pattern: Configuration management
- Facade Pattern: Simplified operation interface
- SOLID Principles: Single Responsibility, Open/Closed, etc.
"""

import os
import platform
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Optional
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


# ============================================================================
# CONFIGURATION - Singleton Pattern
# ============================================================================

class Config:
    """Singleton configuration manager (DRY principle)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.APP_TITLE = "Stardew Valley Cross-Save Tool"
        self.WINDOW_SIZE = (1000, 1000)
        self.MIN_SIZE = (1000, 1000)
        self.BACKUP_ROOT = Path.home() / "StardewValleyCrossSaves_Backups"
        
        # Color palette (Stardew Valley theme)
        self.COLORS = {
            'bg': '#8B4513',
            'bg_dark': '#5D2E0F',
            'bg_light': '#D2B48C',
            'primary': '#5C8A3D',
            'primary_dark': '#3D5A29',
            'accent': '#F4A460',
            'text': '#3E2723',
            'text_light': '#FFFFFF',
            'button': '#8FBC8F',
            'button_hover': '#6B9B6B',
            'button_text': '#2C1810',
            'error': '#C74440',
            'success': '#5C8A3D',
        }
        
        # Font configuration
        self.FONTS = {
            'title': ('Georgia', 20, 'bold'),
            'subtitle': ('Georgia', 13),
            'label': ('Georgia', 16, 'bold'),
            'hint': ('Georgia', 12, 'italic'),
            'button': ('Georgia', 13, 'bold'),
            'button_small': ('Georgia', 11, 'bold'),
            'entry': ('Courier', 11),
            'log': ('Courier', 10),
        }


# ============================================================================
# PLATFORM ABSTRACTION - Strategy Pattern (SOLID: Open/Closed Principle)
# ============================================================================

class LinkStrategy(ABC):
    """Abstract strategy for platform-specific link operations"""
    
    @abstractmethod
    def create_link(self, link_path: Path, target_path: Path) -> None:
        """Create a link from link_path to target_path"""
        pass
    
    @abstractmethod
    def is_link(self, path: Path) -> bool:
        """Check if path is a link/junction"""
        pass
    
    @abstractmethod
    def remove_link(self, path: Path) -> None:
        """Remove a link/junction"""
        pass


class SymlinkStrategy(LinkStrategy):
    """Strategy for Unix-like systems (macOS, Linux)"""
    
    def create_link(self, link_path: Path, target_path: Path) -> None:
        try:
            os.symlink(str(target_path), str(link_path), target_is_directory=True)
        except OSError as e:
            raise RuntimeError(f"Failed to create symlink: {e}")
    
    def is_link(self, path: Path) -> bool:
        try:
            return path.is_symlink()
        except Exception:
            return False
    
    def remove_link(self, path: Path) -> None:
        if path.exists() and self.is_link(path):
            path.unlink()


class JunctionStrategy(LinkStrategy):
    """Strategy for Windows (junction points)"""
    
    def create_link(self, link_path: Path, target_path: Path) -> None:
        cmd = ["cmd", "/c", "mklink", "/J", f'"{link_path}"', f'"{target_path}"']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or "mklink failed"
            raise RuntimeError(f"Failed to create junction: {error_msg}")
    
    def is_link(self, path: Path) -> bool:
        if not path.exists():
            return False
        try:
            cmd = ["cmd", "/c", "fsutil", "reparsepoint", "query", str(path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def remove_link(self, path: Path) -> None:
        if path.exists() and self.is_link(path):
            path.unlink()


class PlatformFactory:
    """Factory for creating platform-specific strategies (Factory Pattern)"""
    
    @staticmethod
    def create_link_strategy() -> LinkStrategy:
        system = platform.system().lower()
        if system.startswith("win"):
            return JunctionStrategy()
        else:
            return SymlinkStrategy()
    
    @staticmethod
    def get_platform_name() -> str:
        system = platform.system().lower()
        if system.startswith("win"):
            return "Windows"
        elif system == "darwin":
            return "macOS"
        else:
            return "Linux"


# ============================================================================
# PATH DETECTION - Strategy Pattern
# ============================================================================

class PathDetector(ABC):
    """Abstract detector for platform-specific paths"""
    
    @abstractmethod
    def get_saves_paths(self) -> list[Path]:
        """Get possible save file locations"""
        pass
    
    @abstractmethod
    def get_install_paths(self) -> list[Path]:
        """Get possible game installation paths"""
        pass


class MacOSPathDetector(PathDetector):
    def get_saves_paths(self) -> list[Path]:
        return [
            Path.home() / "Library" / "Application Support" / "StardewValley" / "Saves",
            Path.home() / ".config" / "StardewValley" / "Saves"
        ]
    
    def get_install_paths(self) -> list[Path]:
        return [
            Path("/Applications/Stardew Valley.app"),
            Path.home() / "Applications" / "Stardew Valley.app",
            Path.home() / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Stardew Valley",
            Path("/Applications/Stardew Valley GOG.app")
        ]


class WindowsPathDetector(PathDetector):
    def get_saves_paths(self) -> list[Path]:
        appdata = os.getenv("APPDATA")
        if appdata:
            return [Path(appdata) / "StardewValley" / "Saves"]
        return []
    
    def get_install_paths(self) -> list[Path]:
        paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley"),
            Path("C:/Program Files/Steam/steamapps/common/Stardew Valley"),
            Path("C:/GOG Games/Stardew Valley"),
            Path("C:/Program Files (x86)/GOG Galaxy/Games/Stardew Valley")
        ]
        
        steam_config = Path.home() / "AppData" / "Local" / "Steam"
        if steam_config.exists():
            paths.append(steam_config / "steamapps" / "common" / "Stardew Valley")
        
        return paths


class LinuxPathDetector(PathDetector):
    def get_saves_paths(self) -> list[Path]:
        return [Path.home() / ".config" / "StardewValley" / "Saves"]
    
    def get_install_paths(self) -> list[Path]:
        return [
            Path.home() / ".steam" / "steam" / "steamapps" / "common" / "Stardew Valley",
            Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "Stardew Valley",
            Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam" / "steamapps" / "common" / "Stardew Valley"
        ]


class PathDetectorFactory:
    """Factory for creating platform-specific path detectors"""
    
    @staticmethod
    def create() -> PathDetector:
        system = platform.system().lower()
        if system.startswith("win"):
            return WindowsPathDetector()
        elif system == "darwin":
            return MacOSPathDetector()
        else:
            return LinuxPathDetector()


# ============================================================================
# FILE OPERATIONS - Facade Pattern (KISS Principle)
# ============================================================================

class FileOperations:
    """Facade for file system operations (simplifies complex operations)"""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize and resolve path"""
        return str(Path(path).expanduser().resolve())
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """Create directory if it doesn't exist"""
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if path exists (safe)"""
        try:
            return Path(path).exists()
        except Exception:
            return False
    
    @staticmethod
    def copy_contents(src: Path, dst: Path, overwrite: bool = True) -> None:
        """Copy all contents from src to dst"""
        FileOperations.ensure_directory(dst)
        for item in src.iterdir():
            dst_item = dst / item.name
            if dst_item.exists() and overwrite:
                if dst_item.is_dir():
                    shutil.rmtree(dst_item)
                else:
                    dst_item.unlink()
            if item.is_dir():
                shutil.copytree(item, dst_item)
            else:
                shutil.copy2(item, dst_item)
    
    @staticmethod
    def backup_folder(src: Path, backup_root: Path) -> Path:
        """Create timestamped backup of folder"""
        FileOperations.ensure_directory(backup_root)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dst = backup_root / f"Saves-backup-{timestamp}"
        shutil.copytree(src, dst)
        return dst
    
    @staticmethod
    def remove_path(path: Path) -> None:
        """Remove file or directory"""
        if not path.exists():
            return
        if path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


# ============================================================================
# GAME DETECTION SERVICE (Single Responsibility Principle)
# ============================================================================

class GameDetectionService:
    """Service for detecting game installation and saves"""
    
    def __init__(self, path_detector: PathDetector):
        self.path_detector = path_detector
    
    def find_saves_path(self) -> Optional[Path]:
        """Find game saves directory"""
        for path in self.path_detector.get_saves_paths():
            if path.exists() and path.is_dir():
                return path
        return None
    
    def find_installation(self) -> Optional[Path]:
        """Find game installation directory"""
        for game_path in self.path_detector.get_install_paths():
            if not game_path.exists():
                continue
            
            # Platform-specific validation
            system = platform.system().lower()
            if system == "darwin":
                # Check if it's a .app bundle (macOS)
                if game_path.suffix == ".app":
                    return game_path
                # Or a Steam installation folder (has Contents directory)
                elif (game_path / "Contents").exists():
                    return game_path
                # Or contains a .app bundle
                elif (game_path / "Stardew Valley.app").exists():
                    return game_path
            elif system.startswith("win"):
                exe_path = game_path / "Stardew Valley.exe"
                if exe_path.exists():
                    return game_path
            else:  # Linux
                exe_path = game_path / "Stardew Valley"
                if exe_path.exists():
                    return game_path
        
        return None
    
    def get_platform_hint(self) -> str:
        """Get helpful hint for current platform"""
        system = platform.system().lower()
        if system == "darwin":
            return "macOS: typical Saves = ~/Library/Application Support/StardewValley/Saves"
        elif system.startswith("win"):
            return "Windows: typical Saves = %AppData%\\StardewValley\\Saves"
        else:
            return "Linux: typical Saves = ~/.config/StardewValley/Saves"


# ============================================================================
# COMMAND PATTERN - Undoable Operations
# ============================================================================

class Command(ABC):
    """Abstract command for operations (Command Pattern)"""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command"""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Check if command can be undone"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command"""
        pass


@dataclass
class OperationResult:
    """Result of an operation (Value Object)"""
    success: bool
    message: str
    backup_path: Optional[Path] = None


class MigrateCommand(Command):
    """Command to migrate saves to cloud"""
    
    def __init__(self, game_saves: Path, cloud_saves: Path, logger):
        self.game_saves = game_saves
        self.cloud_saves = cloud_saves
        self.logger = logger
        self.backup_path: Optional[Path] = None
    
    def execute(self) -> OperationResult:
        try:
            self.logger(f"[MIGRATE] Game Saves: {self.game_saves}")
            self.logger(f"[MIGRATE] Cloud Saves: {self.cloud_saves}")
            
            FileOperations.ensure_directory(self.cloud_saves)
            FileOperations.copy_contents(self.game_saves, self.cloud_saves, overwrite=True)
            
            self.logger("[OK] Copy to cloud completed")
            return OperationResult(True, "Migration completed: saves copied to cloud")
        except Exception as e:
            self.logger(f"[ERROR] {e}")
            return OperationResult(False, str(e))
    
    def can_undo(self) -> bool:
        return False  # Migrate doesn't need undo (non-destructive)
    
    def undo(self) -> None:
        pass


class LinkCommand(Command):
    """Command to link saves to cloud"""
    
    def __init__(self, game_saves: Path, cloud_saves: Path, link_strategy: LinkStrategy, 
                 config: Config, logger):
        self.game_saves = game_saves
        self.cloud_saves = cloud_saves
        self.link_strategy = link_strategy
        self.config = config
        self.logger = logger
        self.backup_path: Optional[Path] = None
    
    def execute(self) -> OperationResult:
        try:
            self.logger(f"[LINK] Game Saves: {self.game_saves}")
            self.logger(f"[LINK] Cloud Saves: {self.cloud_saves}")
            
            # Check if already linked
            if self.link_strategy.is_link(self.game_saves):
                return OperationResult(False, 
                    "The game Saves folder appears to already be a link/junction.\n"
                    "Use 'Restore Backup' first to remove it.")
            
            # Ensure cloud folder exists
            FileOperations.ensure_directory(self.cloud_saves)
            self.logger("[INFO] Preparing cloud Saves folder")
            
            # Copy to cloud BEFORE removing local (data safety)
            self.logger("[MIGRATE] Copying saves to cloud...")
            FileOperations.copy_contents(self.game_saves, self.cloud_saves, overwrite=True)
            self.logger("[OK] Saves migrated to cloud")
            
            # Backup local saves
            self.backup_path = FileOperations.backup_folder(
                self.game_saves, self.config.BACKUP_ROOT
            )
            self.logger(f"[BACKUP] Created at: {self.backup_path}")
            
            # Remove original folder
            FileOperations.remove_path(self.game_saves)
            self.logger("[INFO] Removed original Saves folder")
            
            # Create link
            self.link_strategy.create_link(self.game_saves, self.cloud_saves)
            self.logger(f"[OK] Link created: {self.game_saves} -> {self.cloud_saves}")
            
            return OperationResult(True, 
                "Link created! Your saves are now synced via cloud storage.",
                self.backup_path)
        except Exception as e:
            self.logger(f"[ERROR] {e}")
            return OperationResult(False, str(e))
    
    def can_undo(self) -> bool:
        return self.backup_path is not None and self.backup_path.exists()
    
    def undo(self) -> None:
        """Restore from backup"""
        if not self.can_undo():
            raise RuntimeError("No backup available for undo")
        
        # Remove link
        if self.game_saves.exists():
            self.link_strategy.remove_link(self.game_saves)
            FileOperations.remove_path(self.game_saves)
        
        # Restore backup
        shutil.copytree(self.backup_path, self.game_saves)
        self.logger(f"[UNDO] Restored from backup: {self.backup_path}")


class RestoreCommand(Command):
    """Command to restore from backup"""
    
    def __init__(self, game_saves: Path, backup_path: Optional[Path], 
                 link_strategy: LinkStrategy, logger):
        self.game_saves = game_saves
        self.backup_path = backup_path
        self.link_strategy = link_strategy
        self.logger = logger
    
    def execute(self) -> OperationResult:
        try:
            if not self.backup_path or not self.backup_path.exists():
                return OperationResult(False, 
                    "No backup available.\nBackup is only created after 'Link to Cloud'.")
            
            self.logger(f"[RESTORE] From: {self.backup_path}")
            
            # Remove current link/folder
            if self.game_saves.exists():
                FileOperations.remove_path(self.game_saves)
                self.logger("[INFO] Removed current link/folder")
            
            # Restore backup
            shutil.copytree(self.backup_path, self.game_saves)
            self.logger("[OK] Backup restored")
            
            return OperationResult(True, "Restore completed: original saves are back to local")
        except Exception as e:
            self.logger(f"[ERROR] {e}")
            return OperationResult(False, str(e))
    
    def can_undo(self) -> bool:
        return False  # Restore itself is an undo operation
    
    def undo(self) -> None:
        pass


# ============================================================================
# UI FACTORY - Factory Pattern for Widget Creation (DRY Principle)
# ============================================================================

class WidgetFactory:
    """Factory for creating styled widgets (reduces code duplication)"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def create_label(self, parent, text: str, font_key: str = 'label', 
                    fg: str = None, **kwargs) -> tk.Label:
        """Create a styled label"""
        return tk.Label(
            parent,
            text=text,
            font=self.config.FONTS[font_key],
            fg=fg or self.config.COLORS['text'],
            bg=self.config.COLORS['bg_light'],
            **kwargs
        )
    
    def create_entry(self, parent, textvariable, readonly: bool = False, **kwargs) -> tk.Entry:
        """Create a styled entry"""
        state = "readonly" if readonly else "normal"
        bg = '#E8E8E8' if readonly else '#FFFACD'
        return tk.Entry(
            parent,
            textvariable=textvariable,
            state=state,
            font=self.config.FONTS['entry'],
            bg=bg,
            fg=self.config.COLORS['text'],
            relief="solid",
            bd=1,
            **kwargs
        )
    
    def create_button(self, parent, text: str, command, style: str = 'primary', 
                     **kwargs) -> tk.Button:
        """Create a styled button"""
        styles = {
            'primary': {
                'bg': self.config.COLORS['primary_dark'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button']
            },
            'secondary': {
                'bg': self.config.COLORS['bg_dark'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button']
            },
            'small': {
                'bg': self.config.COLORS['button'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button_small']
            },
            'restore': {
                'bg': self.config.COLORS['bg'],
                'fg': self.config.COLORS['primary_dark'],
                'font': self.config.FONTS['button_small']
            }
        }
        
        style_config = styles.get(style, styles['primary'])
        
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=style_config['bg'],
            fg=style_config['fg'],
            font=style_config['font'],
            activebackground=self.config.COLORS['button_hover'],
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=10,
            **kwargs
        )
    
    def create_warning_banner(self, parent, icon: str, title: str, 
                            message: str, bg_color: str) -> tk.Frame:
        """Create a warning/info banner"""
        frame = tk.Frame(parent, bg=bg_color, bd=2, relief="solid")
        
        icon_label = tk.Label(
            frame,
            text=icon,
            font=("Arial", 28),
            bg=bg_color,
            fg=self.config.COLORS['error']
        )
        icon_label.pack(side="left", padx=10, pady=5)
        
        content = tk.Frame(frame, bg=bg_color)
        content.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        
        if title:
            tk.Label(
                content,
                text=title,
                font=("Georgia", 12, "bold"),
                bg=bg_color,
                fg=self.config.COLORS['text'],
                justify="left"
            ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            content,
            text=message,
            font=("Georgia", 10, "bold"),
            bg=bg_color,
            fg='#8B0000' if 'FFE5E5' in bg_color else '#BF360C',
            justify="left",
            wraplength=750
        ).pack(anchor="w")
        
        return frame


# ============================================================================
# MAIN APPLICATION - Template Method Pattern
# ============================================================================

class StardewCrossSaveApp(tk.Tk):
    """Main application (uses composition over inheritance)"""
    
    def __init__(self):
        super().__init__()
        
        # Dependency injection (SOLID: Dependency Inversion)
        self.config = Config()
        self.link_strategy = PlatformFactory.create_link_strategy()
        self.path_detector = PathDetectorFactory.create()
        self.game_detector = GameDetectionService(self.path_detector)
        self.widget_factory = WidgetFactory(self.config)
        
        # State
        self.game_saves_var = tk.StringVar()
        self.cloud_root_var = tk.StringVar()
        self.cloud_saves_var = tk.StringVar()
        self.last_backup: Optional[Path] = None
        
        # Setup window
        self._setup_window()
        self._build_ui()
        self._auto_detect()
    
    def _setup_window(self):
        """Configure main window"""
        self.title(self.config.APP_TITLE)
        self.geometry(f"{self.config.WINDOW_SIZE[0]}x{self.config.WINDOW_SIZE[1]}")
        self.minsize(*self.config.MIN_SIZE)
        self.configure(bg=self.config.COLORS['bg'])
        
        # Set icon
        try:
            icon_path = Path(__file__).parent / "assets" / "logo.png"
            if icon_path.exists():
                icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon)
        except Exception:
            pass
        
        # Background image
        self._load_background()
        self.bind("<Configure>", self._on_resize)
        self.last_size = self.config.WINDOW_SIZE
    
    def _load_background(self):
        """Load background image"""
        try:
            bg_path = Path(__file__).parent / "assets" / "background.jpg"
            if bg_path.exists():
                w, h = self.winfo_width() or self.config.WINDOW_SIZE[0], \
                       self.winfo_height() or self.config.WINDOW_SIZE[1]
                img = Image.open(bg_path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                
                if hasattr(self, 'bg_label'):
                    self.bg_label.configure(image=self.bg_image)
                else:
                    self.bg_label = tk.Label(self, image=self.bg_image)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Background load error: {e}")
    
    def _on_resize(self, event):
        """Handle window resize"""
        if event.widget == self:
            current = (event.width, event.height)
            if abs(current[0] - self.last_size[0]) > 50 or \
               abs(current[1] - self.last_size[1]) > 50:
                self.last_size = current
                self.after(100, self._load_background)
    
    def _build_ui(self):
        """Build user interface (Template Method)"""
        pad = {"padx": 15, "pady": 8}
        
        # Main container
        main_frame = tk.Frame(self, bg='', bd=0)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.96)
        
        container = tk.Frame(main_frame, bg=self.config.COLORS['bg_light'], bd=4, relief="ridge")
        container.pack(fill="both", expand=True)
        
        # Header
        self._build_header(container, pad)
        
        # Warning banners
        self._build_warnings(container)
        
        # Path selection
        self._build_path_selectors(container, pad)
        
        # Action buttons
        self._build_actions(container, pad)
        
        # Log area
        self._build_log(container)
    
    def _build_header(self, parent, pad):
        """Build header with logo and title"""
        header = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        header.pack(fill="x", **pad)
        
        # Logo
        try:
            logo_path = Path(__file__).parent / "assets" / "logo.png"
            if logo_path.exists():
                logo_img = Image.open(logo_path).resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(header, image=self.logo_photo, bg=self.config.COLORS['bg_light']).pack(side="left")
        except Exception:
            pass
        
        # Title
        self.widget_factory.create_label(
            header, self.config.APP_TITLE, 'title', 
            fg=self.config.COLORS['primary_dark']
        ).pack(side="left", padx=10)
        
        # Subtitle
        self.widget_factory.create_label(
            parent, "Link your Saves to Cloud (iCloud/OneDrive/Dropbox)",
            'subtitle'
        ).pack(anchor="w", padx=15, pady=(0, 5))
    
    def _build_warnings(self, parent):
        """Build warning banners"""
        # Backup warning
        banner = self.widget_factory.create_warning_banner(
            parent, "⚠️", "",
            "IMPORTANT: The tool creates automatic backups, but it's recommended\n"
            "to manually backup your saves before proceeding for extra safety!",
            '#FFE5E5'
        )
        banner.pack(fill="x", padx=15, pady=10)
        
        # Version compatibility
        banner = self.widget_factory.create_warning_banner(
            parent, "⚡", "Version Compatibility Warning:",
            "⚠️ IMPORTANT: Before syncing, verify that your PC and Mobile versions match!\n"
            "Mobile updates often lag behind PC. Using incompatible versions may corrupt saves.",
            '#FFF9E6'
        )
        banner.pack(fill="x", padx=15, pady=(0, 10))
    
    def _build_path_selectors(self, parent, pad):
        """Build path selection UI"""
        # Game saves folder
        frame = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        frame.pack(fill="x", **pad)
        
        self.widget_factory.create_label(
            frame, "📁 Game Saves Folder (the 'Saves' folder inside StardewValley):"
        ).pack(anchor="w")
        
        self.widget_factory.create_label(
            frame, "💡 Select the folder where Stardew Valley stores your save files",
            'hint', fg=self.config.COLORS['primary_dark']
        ).pack(anchor="w", padx=5, pady=(2, 5))
        
        row = tk.Frame(frame, bg=self.config.COLORS['bg_light'])
        row.pack(fill="x", pady=5)
        
        self.widget_factory.create_entry(row, self.game_saves_var).pack(
            side="left", fill="x", expand=True
        )
        self.widget_factory.create_button(
            row, "Choose…", self._pick_game_saves, 'small'
        ).pack(side="left", padx=8)
        
        # Cloud folder
        frame = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        frame.pack(fill="x", **pad)
        
        self.widget_factory.create_label(
            frame, "☁️ Cloud Folder (your cloud sync folder, e.g., iCloud/OneDrive):"
        ).pack(anchor="w")
        
        self.widget_factory.create_label(
            frame, "💡 The tool will automatically create a 'Saves' subfolder here",
            'hint', fg=self.config.COLORS['primary_dark']
        ).pack(anchor="w", padx=5, pady=(2, 5))
        
        row = tk.Frame(frame, bg=self.config.COLORS['bg_light'])
        row.pack(fill="x", pady=5)
        
        self.widget_factory.create_entry(row, self.cloud_root_var).pack(
            side="left", fill="x", expand=True
        )
        self.widget_factory.create_button(
            row, "Choose…", self._pick_cloud_root, 'small'
        ).pack(side="left", padx=8)
        
        # Cloud target (readonly)
        frame = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        frame.pack(fill="x", **pad)
        
        self.widget_factory.create_label(
            frame, "Cloud Target (auto-generated):"
        ).pack(anchor="w")
        
        self.widget_factory.create_entry(
            frame, self.cloud_saves_var, readonly=True
        ).pack(fill="x", pady=5)
    
    def _build_actions(self, parent, pad):
        """Build action buttons"""
        # Separator
        tk.Frame(parent, height=2, bg=self.config.COLORS['primary'], 
                relief="sunken").pack(fill="x", padx=15, pady=15)
        
        actions = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        actions.pack(fill="x", **pad)
        
        self.widget_factory.create_label(
            actions, "Choose your action:", font_key='label'
        ).pack(anchor="w", pady=(0, 5))
        
        self.widget_factory.create_label(
            actions, 
            "• Copy Only: backup to cloud without linking  •  Link to Cloud: full sync setup (recommended)",
            'hint', fg=self.config.COLORS['primary_dark']
        ).pack(anchor="w", pady=(0, 10))
        
        # Main buttons
        button_row = tk.Frame(actions, bg=self.config.COLORS['bg_light'])
        button_row.pack(fill="x", pady=(0, 10))
        
        self.widget_factory.create_button(
            button_row, "📋 Copy to Cloud Only", self._migrate_to_cloud, 'secondary'
        ).pack(side="left", padx=5, expand=True, fill="x")
        
        self.widget_factory.create_button(
            button_row, "🔗 Link to Cloud", self._link_to_cloud, 'primary'
        ).pack(side="left", padx=5, expand=True, fill="x")
        
        # Restore button
        restore_row = tk.Frame(actions, bg=self.config.COLORS['bg_light'])
        restore_row.pack(fill="x")
        
        self.widget_factory.create_button(
            restore_row, "♻️ Restore from Backup", self._restore_backup, 'restore'
        ).pack(side="right", padx=5)
    
    def _build_log(self, parent):
        """Build log area"""
        self.widget_factory.create_label(
            parent, "Status Log:", font_key='hint'
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        log_frame = tk.Frame(parent, bg=self.config.COLORS['bg_light'])
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.log = tk.Text(
            log_frame, height=10, wrap="word",
            font=self.config.FONTS['log'],
            bg='#FFFEF0', fg=self.config.COLORS['text'],
            relief="solid", bd=1, highlightthickness=0
        )
        scrollbar = tk.Scrollbar(log_frame, command=self.log.yview)
        self.log.config(yscrollcommand=scrollbar.set)
        
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._log(self.game_detector.get_platform_hint())
    
    def _log(self, message: str):
        """Log message to text widget"""
        self.log.insert("end", message + "\n")
        self.log.see("end")
    
    def _auto_detect(self):
        """Auto-detect game installation and saves"""
        # Detect installation
        try:
            game_path = self.game_detector.find_installation()
            if game_path:
                self._log(f"[AUTO-DETECT] Game found at: {game_path}")
            else:
                messagebox.showwarning(
                    self.config.APP_TITLE,
                    "Stardew Valley installation not detected.\n\n"
                    "The tool will still work, but you'll need to manually select paths.\n"
                    "Make sure the game is installed before syncing saves."
                )
        except Exception as e:
            self._log(f"[WARNING] Game detection error: {e}")
        
        # Detect saves
        saves_path = self.game_detector.find_saves_path()
        if saves_path:
            self.game_saves_var.set(str(saves_path))
            self._log(f"[AUTO-DETECT] Saves found at: {saves_path}")
            self._recompute_cloud_target()
        else:
            self._log("[INFO] Saves not auto-detected. Select manually.")
    
    def _recompute_cloud_target(self):
        """Recompute cloud saves path"""
        cloud_root = self.cloud_root_var.get().strip()
        if cloud_root:
            self.cloud_saves_var.set(FileOperations.normalize_path(
                str(Path(cloud_root) / "Saves")
            ))
        else:
            self.cloud_saves_var.set("")
    
    def _pick_game_saves(self):
        """Pick game saves folder"""
        path = filedialog.askdirectory(title="Select the game Saves folder")
        if path:
            self.game_saves_var.set(FileOperations.normalize_path(path))
            self._recompute_cloud_target()
    
    def _pick_cloud_root(self):
        """Pick cloud root folder"""
        path = filedialog.askdirectory(title="Select the Cloud folder")
        if path:
            self.cloud_root_var.set(FileOperations.normalize_path(path))
            self._recompute_cloud_target()
    
    def _validate_paths(self) -> tuple[Path, Path, Path]:
        """Validate selected paths"""
        game_saves = self.game_saves_var.get().strip()
        cloud_root = self.cloud_root_var.get().strip()
        cloud_saves = self.cloud_saves_var.get().strip()
        
        if not game_saves or not cloud_root:
            raise ValueError("Select both game Saves and Cloud folders")
        if not FileOperations.path_exists(game_saves):
            raise ValueError("Game Saves folder doesn't exist")
        if not FileOperations.path_exists(cloud_root):
            raise ValueError("Cloud folder doesn't exist")
        if not cloud_saves:
            raise ValueError("Invalid cloud target")
        
        return Path(game_saves), Path(cloud_root), Path(cloud_saves)
    
    def _migrate_to_cloud(self):
        """Execute migrate command"""
        try:
            game_saves, _, cloud_saves = self._validate_paths()
            
            command = MigrateCommand(game_saves, cloud_saves, self._log)
            result = command.execute()
            
            if result.success:
                messagebox.showinfo(self.config.APP_TITLE, result.message)
            else:
                messagebox.showerror(self.config.APP_TITLE, result.message)
        except Exception as e:
            messagebox.showerror(self.config.APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")
    
    def _link_to_cloud(self):
        """Execute link command"""
        try:
            game_saves, _, cloud_saves = self._validate_paths()
            
            command = LinkCommand(game_saves, cloud_saves, self.link_strategy, 
                                self.config, self._log)
            result = command.execute()
            
            if result.success:
                self.last_backup = result.backup_path
                messagebox.showinfo(self.config.APP_TITLE, result.message)
            else:
                messagebox.showerror(self.config.APP_TITLE, result.message)
        except Exception as e:
            messagebox.showerror(self.config.APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")
    
    def _restore_backup(self):
        """Execute restore command"""
        try:
            game_saves = self.game_saves_var.get().strip()
            if not game_saves:
                raise ValueError("Select game Saves folder first")
            
            command = RestoreCommand(Path(game_saves), self.last_backup, 
                                   self.link_strategy, self._log)
            result = command.execute()
            
            if result.success:
                messagebox.showinfo(self.config.APP_TITLE, result.message)
            else:
                messagebox.showerror(self.config.APP_TITLE, result.message)
        except Exception as e:
            messagebox.showerror(self.config.APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Application entry point"""
    try:
        app = StardewCrossSaveApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
