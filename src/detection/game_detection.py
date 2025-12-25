"""Game Detection Service - Detects game installation and saves (SRP)"""

import platform
from pathlib import Path
from typing import Optional
from .path_detector import PathDetector


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
