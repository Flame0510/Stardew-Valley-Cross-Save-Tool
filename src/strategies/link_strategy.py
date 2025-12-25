"""Link Strategy - Platform-specific link operations (Strategy Pattern)"""

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


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
