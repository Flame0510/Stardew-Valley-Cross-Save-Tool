"""Detection modules - Path and game detection"""

from .path_detector import (
    PathDetector, 
    MacOSPathDetector, 
    WindowsPathDetector, 
    LinuxPathDetector,
    PathDetectorFactory
)
from .game_detection import GameDetectionService

__all__ = [
    'PathDetector', 
    'MacOSPathDetector', 
    'WindowsPathDetector', 
    'LinuxPathDetector',
    'PathDetectorFactory',
    'GameDetectionService'
]
