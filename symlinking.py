#!/usr/bin/env python3
# Stardew Cross Saves Linker
# - macOS/Linux: symlink (ln -s)
# - Windows: junction (mklink /J)
#
# Uso: GUI per scegliere cartella "Saves" del gioco e cartella cloud.
# Crea un collegamento: Saves -> Cloud/Saves (cioè i save stanno nel cloud).
#
# Requisiti: Python 3.x (tkinter incluso di solito)

import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

APP_TITLE = "Stardew Cross Saves Linker"

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
    os.symlink(str(target_path), str(link_path), target_is_directory=True)

def create_junction_windows(link_path: Path, target_path: Path):
    # mklink /J "link" "target"
    cmd = ["cmd", "/c", "mklink", "/J", str(link_path), str(target_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip() or "mklink failed")

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

def pretty_platform_hint() -> str:
    if is_macos():
        return "macOS: tipico Saves = ~/Library/Application Support/StardewValley/Saves oppure ~/.config/StardewValley/Saves"
    if is_windows():
        return "Windows: tipico Saves = %AppData%\\StardewValley\\Saves"
    return "Linux: tipico Saves = ~/.config/StardewValley/Saves"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("840x420")

        self.game_saves_var = tk.StringVar(value="")
        self.cloud_root_var = tk.StringVar(value="")
        self.cloud_saves_var = tk.StringVar(value="")  # computed

        self.status_var = tk.StringVar(value=pretty_platform_hint())

        self._build()

    def _build(self):
        pad = {"padx": 10, "pady": 6}

        header = tk.Label(self, text="Collega StardewValley/Saves a una cartella Cloud (iCloud/OneDrive/Dropbox)", font=("Helvetica", 14))
        header.pack(anchor="w", **pad)

        # Game Saves
        frm1 = tk.Frame(self)
        frm1.pack(fill="x", **pad)

        tk.Label(frm1, text="Cartella Saves del gioco (quella che Stardew usa):").pack(anchor="w")
        row1 = tk.Frame(frm1)
        row1.pack(fill="x")
        e1 = tk.Entry(row1, textvariable=self.game_saves_var)
        e1.pack(side="left", fill="x", expand=True)
        tk.Button(row1, text="Scegli…", command=self.pick_game_saves).pack(side="left", padx=8)

        # Cloud Root
        frm2 = tk.Frame(self)
        frm2.pack(fill="x", **pad)

        tk.Label(frm2, text="Cartella Cloud (es. StardewValleyCrossSaves):").pack(anchor="w")
        row2 = tk.Frame(frm2)
        row2.pack(fill="x")
        e2 = tk.Entry(row2, textvariable=self.cloud_root_var)
        e2.pack(side="left", fill="x", expand=True)
        tk.Button(row2, text="Scegli…", command=self.pick_cloud_root).pack(side="left", padx=8)

        # Preview target
        frm3 = tk.Frame(self)
        frm3.pack(fill="x", **pad)

        tk.Label(frm3, text="Target cloud per i Saves (verrà usato come destinazione):").pack(anchor="w")
        row3 = tk.Frame(frm3)
        row3.pack(fill="x")
        e3 = tk.Entry(row3, textvariable=self.cloud_saves_var, state="readonly")
        e3.pack(side="left", fill="x", expand=True)

        # Options / Actions
        frm4 = tk.Frame(self)
        frm4.pack(fill="x", **pad)

        tk.Button(frm4, text="1) Migra: copia i Saves attuali nel cloud", command=self.migrate_to_cloud).pack(side="left", padx=6)
        tk.Button(frm4, text="2) Collega: fai puntare Saves -> cloud", command=self.link_game_to_cloud).pack(side="left", padx=6)
        tk.Button(frm4, text="Ripristina (rimuove link e rimette backup)", command=self.restore_backup).pack(side="left", padx=6)

        # Status / Logs
        sep = tk.Frame(self, height=1, bg="#ccc")
        sep.pack(fill="x", padx=10, pady=10)

        tk.Label(self, text="Stato:").pack(anchor="w", padx=10)
        self.log = tk.Text(self, height=10, wrap="word")
        self.log.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self._log(self.status_var.get())

        self.backup_path: Path | None = None

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
        path = filedialog.askdirectory(title="Seleziona la cartella Saves del gioco")
        if path:
            self.game_saves_var.set(norm(path))
            self._recompute_cloud_saves()

    def pick_cloud_root(self):
        path = filedialog.askdirectory(title="Seleziona la cartella Cloud (root progetto)")
        if path:
            self.cloud_root_var.set(norm(path))
            self._recompute_cloud_saves()

    def _validate_paths(self):
        game_saves = self.game_saves_var.get().strip()
        cloud_root = self.cloud_root_var.get().strip()
        cloud_saves = self.cloud_saves_var.get().strip()

        if not game_saves or not cloud_root:
            raise ValueError("Seleziona sia la cartella Saves del gioco che la cartella Cloud.")
        if not path_exists(game_saves):
            raise ValueError("La cartella Saves del gioco non esiste.")
        if not path_exists(cloud_root):
            raise ValueError("La cartella Cloud non esiste.")
        if not cloud_saves:
            raise ValueError("Target cloud non valido.")

        return Path(game_saves), Path(cloud_root), Path(cloud_saves)

    def migrate_to_cloud(self):
        try:
            game_saves, _, cloud_saves = self._validate_paths()

            self._log(f"[MIGRA] Game Saves: {game_saves}")
            self._log(f"[MIGRA] Cloud Saves: {cloud_saves}")

            ensure_dir(str(cloud_saves))

            # Copia il contenuto del Saves locale nel cloud
            copy_contents(game_saves, cloud_saves, overwrite=True)
            self._log("[OK] Copia completata nel cloud (overwrite).")

            messagebox.showinfo(APP_TITLE, "Migrazione completata: i Saves locali sono stati copiati nel cloud.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERRORE] {e}")

    def link_game_to_cloud(self):
        try:
            game_saves, _, cloud_saves = self._validate_paths()

            self._log(f"[LINK] Game Saves: {game_saves}")
            self._log(f"[LINK] Cloud Saves: {cloud_saves}")

            # Se game_saves è già link/junction, avvisa
            if is_link(game_saves) or is_junction_windows(game_saves):
                raise RuntimeError("La cartella Saves del gioco sembra già essere un link/junction. Se vuoi rifare, ripristina prima.")

            # Assicurati che la cartella cloud esista
            ensure_dir(str(cloud_saves))
            self._log("[INFO] Preparazione cartella cloud/Saves.")

            # IMPORTANTE: Copia i salvataggi nel cloud PRIMA di rimuovere la cartella locale
            self._log("[MIGRA] Copio i salvataggi nel cloud...")
            copy_contents(game_saves, cloud_saves, overwrite=True)
            self._log("[OK] Salvataggi migrati nel cloud.")

            # Backup del Saves locale (intera cartella)
            backups_root = Path.home() / "StardewValleyCrossSaves_Backups"
            self.backup_path = backup_folder(game_saves, backups_root)
            self._log(f"[BACKUP] Creato backup in: {self.backup_path}")

            # Rimuovi la cartella Saves originale
            remove_path(game_saves)
            self._log("[INFO] Rimossa cartella Saves originale (dopo backup e migrazione).")

            # Crea link -> cloud_saves
            if is_windows():
                create_junction_windows(game_saves, cloud_saves)
                self._log("[OK] Creata junction (mklink /J).")
            else:
                create_symlink_dir(game_saves, cloud_saves)
                self._log("[OK] Creato symlink (os.symlink).")

            messagebox.showinfo(APP_TITLE, "Collegamento creato!\nI tuoi salvataggi sono stati migrati nel cloud e ora Stardew li userà da lì.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERRORE] {e}")

    def restore_backup(self):
        try:
            game_saves = self.game_saves_var.get().strip()
            if not game_saves:
                raise ValueError("Seleziona prima la cartella Saves del gioco.")
            game_saves_p = Path(game_saves)

            if not self.backup_path or not self.backup_path.exists():
                raise RuntimeError("Non ho un backup in memoria. Se hai un backup, ripristinalo manualmente dalla cartella ~/StardewValleyCrossSaves_Backups")

            self._log(f"[RESTORE] Ripristino da: {self.backup_path}")

            # Rimuovi link/junction o cartella attuale
            if game_saves_p.exists():
                remove_path(game_saves_p)
                self._log("[INFO] Rimossa Saves corrente (link o cartella).")

            # Ripristina backup
            shutil.copytree(self.backup_path, game_saves_p)
            self._log("[OK] Backup ripristinato nella posizione originale.")

            messagebox.showinfo(APP_TITLE, "Ripristino completato: i Saves originali sono tornati locali.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))
            self._log(f"[ERRORE] {e}")

def main():
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
