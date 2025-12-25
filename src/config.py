"""Configuration module - Singleton Pattern"""

from pathlib import Path


class Config:
    """Singleton configuration manager (DRY principle)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.APP_TITLE = "Stardew Valley Cross-Save Tool"
        self.WINDOW_SIZE = (1000, 1000)
        self.MIN_SIZE = (1000, 1000)
        self.BACKUP_ROOT = Path.home() / "StardewValleyCrossSaves_Backups"
        
        # Color palette (Stardew Valley theme)
        self.COLORS = {
            'bg': '#8B4513',
            'bg_dark': '#5D2E0F',
            'bg_light': '#D2B48C',
            'primary': '#5C8A3D',
            'primary_dark': '#3D5A29',
            'accent': '#F4A460',
            'text': '#3E2723',
            'text_light': '#FFFFFF',
            'button': '#8FBC8F',
            'button_hover': '#6B9B6B',
            'button_text': '#2C1810',
            'error': '#C74440',
            'success': '#5C8A3D',
        }
        
        # Font configuration
        self.FONTS = {
            'title': ('Georgia', 20, 'bold'),
            'subtitle': ('Georgia', 13),
            'label': ('Georgia', 16, 'bold'),
            'hint': ('Georgia', 12, 'italic'),
            'button': ('Georgia', 13, 'bold'),
            'button_small': ('Georgia', 11, 'bold'),
            'entry': ('Courier', 11),
            'log': ('Courier', 10),
        }
