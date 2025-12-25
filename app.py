#!/usr/bin/env python3
# Stardew Valley Cross Saves Tool
# - macOS/Linux: symlink (ln -s)
# - Windows: junction (mklink /J)
#
# Usage: GUI to select game "Saves" folder and cloud folder.
# Creates a link: Saves -> Cloud/Saves (saves will be stored in the cloud).
#
# Requirements: Python 3.x (tkinter usually included)

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

APP_TITLE = "Stardew Valley Cross-Save Tool"

# Stardew Valley color palette
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
    'button_hover': '#6B9B6B', # Darker green on hover
    'button_text': '#2C1810',  # Very dark brown for button text
    'error': '#C74440',        # Red
    'success': '#5C8A3D',      # Green
}

def is_windows() -> bool:
    return platform.system().lower().startswith("win")

def is_macos() -> bool:
    return platform.system().lower() == "darwin"

def norm(p: str) -> str:
    return str(Path(p).expanduser().resolve())

def path_exists(p: str) -> bool:
    try:
        return Path(p).exists()
    except Exception:
        return False

def is_link(p: Path) -> bool:
    try:
        return p.is_symlink()
    except Exception:
        return False

def is_junction_windows(p: Path) -> bool:
    # Junctions are directory reparse points; Python doesn't always treat them as symlinks.
    if not is_windows() or not p.exists():
        return False
    try:
        # "dir /AL" shows reparse points; but easiest: check if it's a reparse point via attrib
        # We'll use: fsutil reparsepoint query <path> (works on Windows, may require admin).
        cmd = ["cmd", "/c", "fsutil", "reparsepoint", "query", str(p)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False

def ensure_dir(p: str):
    Path(p).mkdir(parents=True, exist_ok=True)

def backup_folder(src: Path, backups_root: Path) -> Path:
    ensure_dir(str(backups_root))
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = backups_root / f"Saves-backup-{ts}"
    shutil.copytree(src, dst)
    return dst

def remove_path(p: Path):
    if not p.exists():
        return
    if p.is_symlink():
        p.unlink()
        return
    if p.is_dir():
        shutil.rmtree(p)
        return
    p.unlink()

def create_symlink_dir(link_path: Path, target_path: Path):
    # link_path becomes a symlink pointing to target_path
    try:
        os.symlink(str(target_path), str(link_path), target_is_directory=True)
    except OSError as e:
        raise RuntimeError(f"Failed to create symlink: {e}")

def create_junction_windows(link_path: Path, target_path: Path):
    # mklink /J "link" "target"
    # Quote paths to handle spaces
    cmd = ["cmd", "/c", "mklink", "/J", f'"{link_path}"', f'"{target_path}"']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        error_msg = r.stderr.strip() or r.stdout.strip() or "mklink failed"
        raise RuntimeError(f"Failed to create junction: {error_msg}")

def copy_contents(src_dir: Path, dst_dir: Path, overwrite: bool = True):
    ensure_dir(str(dst_dir))
    for item in src_dir.iterdir():
        dst = dst_dir / item.name
        if dst.exists() and overwrite:
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)

def get_possible_saves_paths() -> list[Path]:
    """Returns list of possible Stardew Valley Saves paths for current platform"""
    paths = []
    
    if is_macos():
        # macOS paths
        paths.append(Path.home() / "Library" / "Application Support" / "StardewValley" / "Saves")
        paths.append(Path.home() / ".config" / "StardewValley" / "Saves")
    elif is_windows():
        # Windows path
        appdata = os.getenv("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "StardewValley" / "Saves")
    else:
        # Linux path
        paths.append(Path.home() / ".config" / "StardewValley" / "Saves")
    
    return paths

def find_game_saves_path() -> Path | None:
    """Auto-detect Stardew Valley Saves folder if it exists"""
    for path in get_possible_saves_paths():
        if path.exists() and path.is_dir():
            return path
    return None

def get_game_install_paths() -> list[Path]:
    """Returns list of possible Stardew Valley game installation paths"""
    paths = []
    
    if is_macos():
        # macOS app bundles
        paths.append(Path("/Applications/Stardew Valley.app"))
        paths.append(Path.home() / "Applications" / "Stardew Valley.app")
        # Steam
        paths.append(Path.home() / "Library" / "Application Support" / "Steam" / "steamapps" / "common" / "Stardew Valley")
        # GOG
        paths.append(Path("/Applications/Stardew Valley GOG.app"))
    elif is_windows():
        # Steam paths
        program_files = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Stardew Valley"),
            Path("C:/Program Files/Steam/steamapps/common/Stardew Valley"),
        ]
        paths.extend(program_files)
        
        # Try to find Steam library folders
        steam_config = Path.home() / "AppData" / "Local" / "Steam"
        if steam_config.exists():
            paths.append(steam_config / "steamapps" / "common" / "Stardew Valley")
        
        # GOG default path
        paths.append(Path("C:/GOG Games/Stardew Valley"))
        paths.append(Path("C:/Program Files (x86)/GOG Galaxy/Games/Stardew Valley"))
    else:
        # Linux paths
        # Steam
        paths.append(Path.home() / ".steam" / "steam" / "steamapps" / "common" / "Stardew Valley")
        paths.append(Path.home() / ".local" / "share" / "Steam" / "steamapps" / "common" / "Stardew Valley")
        # Flatpak
        paths.append(Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam" / "steamapps" / "common" / "Stardew Valley")
    
    return paths

def find_game_installation() -> Path | None:
    """
    Auto-detect Stardew Valley installation.
    Returns: install_path or None if not found
    """
    for game_path in get_game_install_paths():
        if not game_path.exists():
            continue
        
        if is_macos():
            # Check if it's an app bundle
            if game_path.suffix == ".app":
                # Verify it's actually the game by checking for the executable
                exe_path = game_path / "Contents" / "MacOS" / "Stardew Valley"
                if exe_path.exists():
                    return game_path
            else:
                # Steam installation (not .app bundle)
                exe_path = game_path / "Contents" / "MacOS" / "Stardew Valley"
                if exe_path.exists():
                    return game_path
        
        elif is_windows():
            # Look for executable
            exe_path = game_path / "Stardew Valley.exe"
            if exe_path.exists():
                return game_path
        
        else:
            # Linux - look for executable
            exe_path = game_path / "Stardew Valley"
            if exe_path.exists():
                return game_path
    
    return None

def pretty_platform_hint() -> str:
    if is_macos(): 
        return "macOS: typical Saves = ~/Library/Application Support/StardewValley/Saves or ~/.config/StardewValley/Saves"
    if is_windows():
        return "Windows: typical Saves = %AppData%\\StardewValley\\Saves"
    return "Linux: typical Saves = ~/.config/StardewValley/Saves"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x1000")
        self.minsize(1000, 1000)  # Minimum window size
        self.configure(bg=COLORS['bg'])
        
        # Set window icon
        try:
            icon_path = Path(__file__).parent / "assets" / "logo.png"
            if icon_path.exists():
                icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon)
        except Exception:
            pass

        self.game_saves_var = tk.StringVar(value="")
        self.cloud_root_var = tk.StringVar(value="")
        self.cloud_saves_var = tk.StringVar(value="")  # computed

        self.status_var = tk.StringVar(value=pretty_platform_hint())
        
        # Load background image
        self.bg_image = None
        self.bg_label = None
        try:
            bg_path = Path(__file__).parent / "assets" / "background.jpg"
            if bg_path.exists():
                self.bg_path = bg_path
                self._load_background()
        except Exception as e:
            print(f"Could not load background: {e}")
        
        # Bind resize event
        self.bind("<Configure>", self._on_resize)
        self.last_size = (1100, 850)

        self._build()
        self._auto_detect_saves()
    
    def _load_background(self):
        """Load and resize background image"""
        try:
            if hasattr(self, 'bg_path') and self.bg_path.exists():
                w = self.winfo_width() or 1100
                h = self.winfo_height() or 850
                img = Image.open(self.bg_path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                if self.bg_label:
                    self.bg_label.config(image=self.bg_image)
        except Exception as e:
            print(f"Error loading background: {e}")
    
    def _on_resize(self, event):
        """Handle window resize"""
        if event.widget == self:
            current_size = (event.width, event.height)
            # Only reload if size changed significantly (avoid too many reloads)
            if abs(current_size[0] - self.last_size[0]) > 50 or abs(current_size[1] - self.last_size[1]) > 50:
                self.last_size = current_size
                self.after(100, self._load_background)

    def _build(self):
        pad = {"padx": 15, "pady": 8}
        
        # Background
        if self.bg_image:
            self.bg_label = tk.Label(self, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Main container with responsive placement
        main_frame = tk.Frame(self, bg='', bd=0)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.96)
        
        container = tk.Frame(main_frame, bg=COLORS['bg_light'], bd=4, relief="ridge")
        container.pack(fill="both", expand=True)

        # Header with logo
        header_frame = tk.Frame(container, bg=COLORS['bg_light'])
        header_frame.pack(fill="x", **pad)
        
        try:
            logo_path = Path(__file__).parent / "assets" / "logo.png"
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=self.logo_photo, bg=COLORS['bg_light'])
                logo_label.pack(side="left", padx=10)
        except Exception:
            pass
        
        title_label = tk.Label(
            header_frame, 
            text=APP_TITLE,
            font=("Georgia", 20, "bold"),
            fg=COLORS['primary_dark'],
            bg=COLORS['bg_light']
        )
        title_label.pack(side="left", padx=10)
        
        subtitle = tk.Label(
            container,
            text="Link your Saves to Cloud (iCloud/OneDrive/Dropbox)",
            font=("Georgia", 13),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        )
        subtitle.pack(anchor="w", padx=15, pady=(0, 5))
        
        # WARNING BANNER - BACKUP REMINDER
        warning_frame = tk.Frame(container, bg='#FFE5E5', bd=2, relief="solid")
        warning_frame.pack(fill="x", padx=15, pady=10)
        
        warning_icon = tk.Label(
            warning_frame,
            text="⚠️",
            font=("Arial", 28),
            bg='#FFE5E5',
            fg='#C74440'
        )
        warning_icon.pack(side="left", padx=10, pady=5)
        
        warning_text = tk.Label(
            warning_frame,
            text="IMPORTANT: The tool creates automatic backups, but it's recommended\nto manually backup your saves before proceeding for extra safety!",
            font=("Georgia", 11, "bold"),
            bg='#FFE5E5',
            fg='#8B0000',
            justify="left"
        )
        warning_text.pack(side="left", padx=5, pady=8)

        # VERSION COMPATIBILITY WARNING
        compat_frame = tk.Frame(container, bg='#FFF9E6', bd=2, relief="solid")
        compat_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        compat_icon = tk.Label(
            compat_frame,
            text="⚡",
            font=("Arial", 28),
            bg='#FFF9E6',
            fg='#F57C00'
        )
        compat_icon.pack(side="left", padx=10, pady=5)
        
        compat_content = tk.Frame(compat_frame, bg='#FFF9E6')
        compat_content.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        
        tk.Label(
            compat_content,
            text="Version Compatibility Warning:",
            font=("Georgia", 12, "bold"),
            bg='#FFF9E6',
            fg=COLORS['text'],
            justify="left"
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            compat_content,
            text="⚠️ IMPORTANT: Before syncing, verify that your PC and Mobile versions match!\nMobile updates often lag behind PC. Using incompatible versions may corrupt saves.",
            font=("Georgia", 10, "bold"),
            bg='#FFF9E6',
            fg='#BF360C',
            justify="left",
            wraplength=750
        ).pack(anchor="w")

        # Game Saves
        frm1 = tk.Frame(container, bg=COLORS['bg_light'])
        frm1.pack(fill="x", **pad)

        label1 = tk.Label(
            frm1, 
            text="📁 Game Saves Folder (the 'Saves' folder inside StardewValley):",
            font=("Georgia", 16, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        )
        label1.pack(anchor="w")
        
        hint1 = tk.Label(
            frm1,
            text="💡 Select the folder where Stardew Valley stores your save files",
            font=("Georgia", 12, "italic"),
            fg=COLORS['primary_dark'],
            bg=COLORS['bg_light']
        )
        hint1.pack(anchor="w", padx=5, pady=(2,5))
        
        row1 = tk.Frame(frm1, bg=COLORS['bg_light'])
        row1.pack(fill="x", pady=5)
        e1 = tk.Entry(
            row1, 
            textvariable=self.game_saves_var,
            font=("Courier", 11),
            bg='#FFFACD',
            fg=COLORS['text'],
            relief="solid",
            bd=1
        )
        e1.pack(side="left", fill="x", expand=True)
        
        btn1 = tk.Button(
            row1, 
            text="Choose…",
            command=self.pick_game_saves,
            font=("Georgia", 11, "bold"),
            bg=COLORS['button'],
            fg=COLORS['button_text'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['button_text'],
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=10
        )
        btn1.pack(side="left", padx=8)

        # Cloud Root
        frm2 = tk.Frame(container, bg=COLORS['bg_light'])
        frm2.pack(fill="x", **pad)

        label2 = tk.Label(
            frm2, 
            text="☁️ Cloud Folder (your cloud sync folder, e.g., iCloud/OneDrive):",
            font=("Georgia", 16, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        )
        label2.pack(anchor="w")
        
        hint2 = tk.Label(
            frm2,
            text="💡 The tool will automatically create a 'Saves' subfolder here",
            font=("Georgia", 12, "italic"),
            fg=COLORS['primary_dark'],
            bg=COLORS['bg_light']
        )
        hint2.pack(anchor="w", padx=5, pady=(2,5))
        
        row2 = tk.Frame(frm2, bg=COLORS['bg_light'])
        row2.pack(fill="x", pady=5)
        e2 = tk.Entry(
            row2, 
            textvariable=self.cloud_root_var,
            font=("Courier", 11),
            bg='#FFFACD',
            fg=COLORS['text'],
            relief="solid",
            bd=1
        )
        e2.pack(side="left", fill="x", expand=True)
        
        btn2 = tk.Button(
            row2, 
            text="Choose…",
            command=self.pick_cloud_root,
            font=("Georgia", 11, "bold"),
            bg=COLORS['button'],
            fg=COLORS['button_text'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['button_text'],
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=10
        )
        btn2.pack(side="left", padx=8)

        # Preview target
        frm3 = tk.Frame(container, bg=COLORS['bg_light'])
        frm3.pack(fill="x", **pad)

        tk.Label(
            frm3, 
            text="Cloud Target (auto-generated):",
            font=("Georgia", 16, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        ).pack(anchor="w")
        
        row3 = tk.Frame(frm3, bg=COLORS['bg_light'])
        row3.pack(fill="x", pady=5)
        e3 = tk.Entry(
            row3, 
            textvariable=self.cloud_saves_var, 
            state="readonly",
            font=("Courier", 11),
            bg='#E8E8E8',
            fg=COLORS['text'],
            relief="solid",
            bd=1
        )
        e3.pack(side="left", fill="x", expand=True)

        # Separator
        sep = tk.Frame(container, height=2, bg=COLORS['primary'], relief="sunken")
        sep.pack(fill="x", padx=15, pady=15)

        # Action buttons section
        actions_frame = tk.Frame(container, bg=COLORS['bg_light'])
        actions_frame.pack(fill="x", **pad)
        
        # Instructions
        tk.Label(
            actions_frame,
            text="Choose your action:",
            font=("Georgia", 14, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        ).pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            actions_frame,
            text="• Copy Only: backup to cloud without linking  •  Link to Cloud: full sync setup (recommended)",
            font=("Georgia", 11, "italic"),
            fg=COLORS['primary_dark'],
            bg=COLORS['bg_light']
        ).pack(anchor="w", pady=(0, 10))

        # Main action buttons
        frm4 = tk.Frame(actions_frame, bg=COLORS['bg_light'])
        frm4.pack(fill="x", pady=(0, 10))

        main_buttons = [
            ("📋 Copy to Cloud Only", self.migrate_to_cloud, COLORS['bg_dark'], COLORS['primary_dark']),
            ("🔗 Link to Cloud", self.link_game_to_cloud, COLORS['primary_dark'], COLORS['primary_dark']),
        ]
        
        for text, command, bg_color, fg_color in main_buttons:
            btn = tk.Button(
                frm4, 
                text=text,
                command=command,
                font=("Georgia", 13, "bold"),
                bg=bg_color,
                fg=fg_color,
                activebackground=COLORS['button_hover'],
                activeforeground=COLORS['button_text'],
                relief="solid",
                bd=2,
                cursor="hand2",
                padx=15,
                pady=12
            )
            btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Restore button (separate, less prominent)
        frm5 = tk.Frame(actions_frame, bg=COLORS['bg_light'])
        frm5.pack(fill="x")
        
        restore_btn = tk.Button(
            frm5,
            text="♻️ Restore from Backup",
            command=self.restore_backup,
            font=("Georgia", 11),
            bg=COLORS['bg'],
            fg=COLORS['primary_dark'],
            activebackground=COLORS['bg_dark'],
            activeforeground=COLORS['primary_dark'],
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=8
        )
        restore_btn.pack(side="right", padx=5)

        # Status / Logs
        tk.Label(
            container, 
            text="Status Log:",
            font=("Georgia", 12, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg_light']
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        log_frame = tk.Frame(container, bg=COLORS['bg_light'])
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.log = tk.Text(
            log_frame, 
            height=10, 
            wrap="word",
            font=("Courier", 10),
            bg='#FFFEF0',
            fg=COLORS['text'],
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(log_frame, command=self.log.yview)
        self.log.config(yscrollcommand=scrollbar.set)
        
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._log(self.status_var.get())

        self.backup_path: Path | None = None

    def _auto_detect_saves(self):
        """Auto-detect game saves path and populate field if found"""
        # Check for game installation first
        try:
            game_path = find_game_installation()
            if game_path:
                self._log(f"[GAME FOUND] Stardew Valley installed at: {game_path}")
            else:
                self._log("[INFO] Stardew Valley installation not auto-detected.")
                messagebox.showwarning(
                    APP_TITLE,
                    "Game Not Detected\n\n"
                    "Stardew Valley may not be installed or might be installed in a non-standard location.\n\n"
                    "The tool will still work if you manually select your saves folder."
                )
        except Exception as e:
            self._log(f"[WARNING] Error during game detection: {e}")
        
        # Then check for saves
        detected_path = find_game_saves_path()
        if detected_path:
            self.game_saves_var.set(str(detected_path))
            self._log(f"[AUTO-DETECT] Found game saves at: {detected_path}")
            self._recompute_cloud_saves()
        else:
            self._log("[INFO] Game saves not auto-detected. Please select manually.")

    def _recompute_cloud_saves(self):
        cloud_root = self.cloud_root_var.get().strip()
        if cloud_root:
            self.cloud_saves_var.set(norm(str(Path(cloud_root) / "Saves")))
        else:
            self.cloud_saves_var.set("")

    def _log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def pick_game_saves(self):
        path = filedialog.askdirectory(title="Select the game Saves folder")
        if path:
            self.game_saves_var.set(norm(path))
            self._recompute_cloud_saves()

    def pick_cloud_root(self):
        path = filedialog.askdirectory(title="Select the Cloud folder (project root)")
        if path:
            self.cloud_root_var.set(norm(path))
            self._recompute_cloud_saves()

    def _validate_paths(self):
        game_saves = self.game_saves_var.get().strip()
        cloud_root = self.cloud_root_var.get().strip()
        cloud_saves = self.cloud_saves_var.get().strip()

        if not game_saves or not cloud_root:
            raise ValueError("Select both the game Saves folder and the Cloud folder.")
        if not path_exists(game_saves):
            raise ValueError("The game Saves folder does not exist.")
        if not path_exists(cloud_root):
            raise ValueError("The Cloud folder does not exist.")
        if not cloud_saves:
            raise ValueError("Invalid cloud target.")

        return Path(game_saves), Path(cloud_root), Path(cloud_saves)

    def migrate_to_cloud(self):
        try:
            game_saves, _, cloud_saves = self._validate_paths()

            self._log(f"[MIGRATE] Game Saves: {game_saves}")
            self._log(f"[MIGRATE] Cloud Saves: {cloud_saves}")

            ensure_dir(str(cloud_saves))

            # Copy local Saves content to cloud
            copy_contents(game_saves, cloud_saves, overwrite=True)
            self._log("[OK] Copy to cloud completed (overwrite).")

            messagebox.showinfo(APP_TITLE, "Migration completed: local Saves have been copied to the cloud.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")

    def link_game_to_cloud(self):
        try:
            game_saves, _, cloud_saves = self._validate_paths()

            self._log(f"[LINK] Game Saves: {game_saves}")
            self._log(f"[LINK] Cloud Saves: {cloud_saves}")

            # Check if game_saves is already a link/junction
            if is_link(game_saves) or is_junction_windows(game_saves):
                raise RuntimeError("The game Saves folder appears to already be a link/junction. If you want to redo it, restore first.")

            # Ensure cloud folder exists
            ensure_dir(str(cloud_saves))
            self._log("[INFO] Preparing cloud/Saves folder.")

            # IMPORTANT: Copy saves to cloud BEFORE removing local folder
            self._log("[MIGRATE] Copying saves to cloud...")
            copy_contents(game_saves, cloud_saves, overwrite=True)
            self._log("[OK] Saves migrated to cloud.")

            # Backup local Saves (entire folder)
            backups_root = Path.home() / "StardewValleyCrossSaves_Backups"
            self.backup_path = backup_folder(game_saves, backups_root)
            self._log(f"[BACKUP] Backup created at: {self.backup_path}")

            # Remove original Saves folder
            remove_path(game_saves)
            self._log("[INFO] Removed original Saves folder (after backup and migration).")

            # Create link -> cloud_saves
            if is_windows():
                create_junction_windows(game_saves, cloud_saves)
                self._log("[OK] Created junction (mklink /J).")
            else:
                create_symlink_dir(game_saves, cloud_saves)
                self._log("[OK] Created symlink (os.symlink).")

            messagebox.showinfo(APP_TITLE, "Link created!\nYour saves have been migrated to the cloud and Stardew will now use them from there.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")

    def restore_backup(self):
        try:
            game_saves = self.game_saves_var.get().strip()
            if not game_saves:
                raise ValueError("Select the game Saves folder first.")
            game_saves_p = Path(game_saves)

            if not self.backup_path or not self.backup_path.exists():
                raise RuntimeError("No backup in memory. If you have a backup, restore it manually from ~/StardewValleyCrossSaves_Backups")

            self._log(f"[RESTORE] Restoring from: {self.backup_path}")

            # Remove current link/junction or folder
            if game_saves_p.exists():
                remove_path(game_saves_p)
                self._log("[INFO] Removed current Saves (link or folder).")

            # Restore backup
            shutil.copytree(self.backup_path, game_saves_p)
            self._log("[OK] Backup restored to original location.")

            messagebox.showinfo(APP_TITLE, "Restore completed: original Saves are back to local.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERROR] {e}")

def main():
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
