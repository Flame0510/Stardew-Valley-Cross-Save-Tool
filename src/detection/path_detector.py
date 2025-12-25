"""Path Detector - Platform-specific path detection (Strategy Pattern)"""

import os
import platform
from abc import ABC, abstractmethod
from pathlib import Path


class PathDetector(ABC):
    """Abstract detector for platform-specific paths"""
    
    @abstractmethod
    def get_saves_paths(self) -> list[Path]:
        """Get possible save file paths"""
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
