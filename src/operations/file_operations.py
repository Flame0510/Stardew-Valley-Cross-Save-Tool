"""File Operations - Facade Pattern for file system operations"""

import os
import shutil
import time
from pathlib import Path


class FileOperations:
    """Facade for file system operations (simplifies complex operations)"""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize a path string"""
        return str(Path(path).expanduser().resolve())
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """Ensure directory exists"""
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if path exists"""
        try:
            return Path(path).exists()
        except Exception:
            return False
    
    @staticmethod
    def copy_contents(src: Path, dst: Path, overwrite: bool = True) -> None:
        """Copy contents from src to dst"""
        FileOperations.ensure_directory(dst)
        
        for item in src.iterdir():
            s = src / item.name
            d = dst / item.name
            
            if s.is_dir():
                if d.exists() and overwrite:
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                if d.exists() and overwrite:
                    d.unlink()
                shutil.copy2(s, d)
    
    @staticmethod
    def backup_folder(src: Path, backup_root: Path) -> Path:
        """Create a timestamped backup"""
        FileOperations.ensure_directory(backup_root)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = backup_root / f"backup_{timestamp}"
        shutil.copytree(src, backup_path)
        return backup_path
    
    @staticmethod
    def remove_path(path: Path) -> None:
        """Remove a file or directory"""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
