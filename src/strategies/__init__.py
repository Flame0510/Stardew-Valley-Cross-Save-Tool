"""Strategy Pattern - Platform-specific operations"""

from .link_strategy import LinkStrategy, SymlinkStrategy, JunctionStrategy
from .platform_factory import PlatformFactory

__all__ = ['LinkStrategy', 'SymlinkStrategy', 'JunctionStrategy', 'PlatformFactory']
