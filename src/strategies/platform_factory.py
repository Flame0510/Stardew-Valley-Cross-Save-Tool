"""Platform Factory - Creates platform-specific strategies (Factory Pattern)"""

import platform
from .link_strategy import LinkStrategy, SymlinkStrategy, JunctionStrategy


class PlatformFactory:
    """Factory for creating platform-specific strategies"""
    
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
        if system == "darwin":
            return "macOS"
        elif system.startswith("win"):
            return "Windows"
        else:
            return "Linux"
