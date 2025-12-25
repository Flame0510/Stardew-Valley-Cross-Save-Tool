#!/usr/bin/env python3
"""
Stardew Valley Cross-Save Tool
Main Entry Point
"""

from src.ui import StardewCrossSaveApp


def main():
    """Application entry point"""
    try:
        app = StardewCrossSaveApp()
        app.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
