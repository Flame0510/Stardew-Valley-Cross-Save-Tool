"""Main Window - Main application UI (Template Method Pattern)"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional
from PIL import Image, ImageTk

from .. import __version__
from ..config import Config
from ..strategies import PlatformFactory
from ..detection import PathDetectorFactory, GameDetectionService
from ..operations import FileOperations, MigrateCommand, LinkCommand, RestoreCommand
from .widget_factory import WidgetFactory


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
        self.title(f"{self.config.APP_TITLE} v{__version__}")
        self.geometry(f"{self.config.WINDOW_SIZE[0]}x{self.config.WINDOW_SIZE[1]}")
        self.minsize(*self.config.MIN_SIZE)
        self.configure(bg=self.config.COLORS['bg'])
        
        # Set icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "logo.png"
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
            bg_path = Path(__file__).parent.parent.parent / "assets" / "background.jpg"
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
            logo_path = Path(__file__).parent.parent.parent / "assets" / "logo.png"
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
        ).pack(side="left", padx=(8, 4))
        self.widget_factory.create_button(
            row, "📂 Open", lambda: self._open_folder(self.game_saves_var.get()), 'small'
        ).pack(side="left", padx=(4, 8))
        
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
        ).pack(side="left", padx=(8, 4))
        self.widget_factory.create_button(
            row, "📂 Open", lambda: self._open_folder(self.cloud_root_var.get()), 'small'
        ).pack(side="left", padx=(4, 8))
        
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
    
    def _open_folder(self, path: str):
        """Open folder in file explorer"""
        if not path or not path.strip():
            messagebox.showwarning(self.config.APP_TITLE, "No path selected")
            return
        
        folder_path = Path(path.strip())
        
        # Check if path exists
        if not folder_path.exists():
            messagebox.showerror(
                self.config.APP_TITLE, 
                f"Path does not exist:\n{folder_path}"
            )
            return
        
        # Open in file explorer
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", str(folder_path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(folder_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder_path)])
            
            self._log(f"[INFO] Opened folder: {folder_path}")
        except Exception as e:
            messagebox.showerror(
                self.config.APP_TITLE, 
                f"Failed to open folder:\n{e}"
            )
            self._log(f"[ERROR] Failed to open folder: {e}")
