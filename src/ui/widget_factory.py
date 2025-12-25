"""Widget Factory - Factory Pattern for UI widget creation (DRY)"""

import tkinter as tk
from ..config import Config


class WidgetFactory:
    """Factory for creating styled widgets (reduces code duplication)"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def create_label(self, parent, text: str, font_key: str = 'label', 
                    fg: str = None, **kwargs) -> tk.Label:
        """Create a styled label"""
        return tk.Label(
            parent,
            text=text,
            font=self.config.FONTS[font_key],
            fg=fg or self.config.COLORS['text'],
            bg=self.config.COLORS['bg_light'],
            **kwargs
        )
    
    def create_entry(self, parent, textvariable, readonly: bool = False, **kwargs) -> tk.Entry:
        """Create a styled entry"""
        state = "readonly" if readonly else "normal"
        bg = '#E8E8E8' if readonly else '#FFFACD'
        return tk.Entry(
            parent,
            textvariable=textvariable,
            state=state,
            font=self.config.FONTS['entry'],
            bg=bg,
            fg=self.config.COLORS['text'],
            relief="solid",
            bd=1,
            **kwargs
        )
    
    def create_button(self, parent, text: str, command, style: str = 'primary', 
                     **kwargs) -> tk.Button:
        """Create a styled button"""
        styles = {
            'primary': {
                'bg': self.config.COLORS['primary_dark'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button']
            },
            'secondary': {
                'bg': self.config.COLORS['bg_dark'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button']
            },
            'small': {
                'bg': self.config.COLORS['button'],
                'fg': self.config.COLORS['button_text'],
                'font': self.config.FONTS['button_small']
            },
            'restore': {
                'bg': self.config.COLORS['bg'],
                'fg': self.config.COLORS['primary_dark'],
                'font': self.config.FONTS['button_small']
            }
        }
        
        style_config = styles.get(style, styles['primary'])
        
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=style_config['bg'],
            fg=style_config['fg'],
            font=style_config['font'],
            activebackground=self.config.COLORS['button_hover'],
            relief="solid",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=10,
            **kwargs
        )
    
    def create_warning_banner(self, parent, icon: str, title: str, 
                            message: str, bg_color: str) -> tk.Frame:
        """Create a warning/info banner"""
        frame = tk.Frame(parent, bg=bg_color, bd=2, relief="solid")
        
        icon_label = tk.Label(
            frame,
            text=icon,
            font=("Arial", 28),
            bg=bg_color,
            fg=self.config.COLORS['error']
        )
        icon_label.pack(side="left", padx=10, pady=5)
        
        content = tk.Frame(frame, bg=bg_color)
        content.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        
        if title:
            tk.Label(
                content,
                text=title,
                font=("Georgia", 11, "bold"),
                bg=bg_color,
                fg='#8B0000',
                justify="left"
            ).pack(anchor="w")
        
        tk.Label(
            content,
            text=message,
            font=("Georgia", 10, "bold"),
            bg=bg_color,
            fg='#8B0000' if 'FFE5E5' in bg_color else '#BF360C',
            justify="left",
            wraplength=750
        ).pack(anchor="w")
        
        return frame
