"""Palette management module for PixelSmart"""
import json
from PySide6.QtGui import QColor, Qt


class PaletteManager:
    """Manages color palettes for the pixel art editor"""
    
    def __init__(self):
        # Initialize with 24 slots: 1 transparent + 15 default colors + 8 empty slots
        self.colors = [
            Qt.transparent,     # Slot 0: Always transparent
            QColor("#000000"),  # Black
            QColor("#FFFFFF"),  # White
            QColor("#FF0000"),  # Red
            QColor("#00FF00"),  # Green
            QColor("#0000FF"),  # Blue
            QColor("#FFFF00"),  # Yellow
            QColor("#FF00FF"),  # Magenta
            QColor("#00FFFF"),  # Cyan
            QColor("#808080"),  # Gray
            QColor("#800000"),  # Dark Red
            QColor("#008000"),  # Dark Green
            QColor("#000080"),  # Dark Blue
            QColor("#808000"),  # Dark Yellow
            QColor("#800080"),  # Dark Magenta
            QColor("#008080"),  # Dark Cyan
        ]
        self.current_index = 1  # Start with black as default (index 1, slot 0 is transparent)
    
    def add_color(self, color):
        """Add a new color to the palette (append to end)"""
        if isinstance(color, str):
            color = QColor(color)
        if color.isValid() and color not in self.colors:
            self.colors.append(color)
    
    def set_current_index(self, index):
        """Set the current color by palette index"""
        if 0 <= index < len(self.colors):
            self.current_index = index
    
    def get_current_color(self):
        """Get the currently selected color"""
        return self.get_color(self.current_index)
    
    def remove_color(self, index):
        """Remove a color from the palette by index"""
        if 0 <= index < len(self.colors) and len(self.colors) > 16:  # Keep minimum 16 colors
            del self.colors[index]
            if self.current_index >= len(self.colors):
                self.current_index = len(self.colors) - 1
    
    def get_color(self, index):
        """Get a color from the palette by index"""
        if 0 <= index < len(self.colors):
            return self.colors[index]
        return Qt.transparent
    

    
    def set_current_color_obj(self, color):
        """Set current color to an exact match if exists, or add new"""
        if color in self.colors:
            self.current_index = self.colors.index(color)
        else:
            self.add_color(color)
            self.current_index = len(self.colors) - 1
    
    def save_to_file(self, filepath):
        """Save palette to a JSON file"""
        def get_color_name(c):
            # Handle Qt.transparent specially - it's transparent but .name() returns "#000000"
            if c == Qt.transparent:
                return '#00000000'  # ARGB format with alpha=0
            elif hasattr(c, 'name') and callable(getattr(c, 'name', None)):
                return c.name()
            else:
                return '#000000'
        
        palette_data = {
            "colors": [get_color_name(color) for color in self.colors],
            "current_index": self.current_index
        }
        with open(filepath, 'w') as f:
            json.dump(palette_data, f, indent=2)
    
    def load_from_file(self, filepath):
        """Load palette from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                palette_data = json.load(f)
            
            def load_color(c):
                # Handle special transparent color saved as "#00000000"
                if c == '#00000000':
                    return Qt.transparent
                else:
                    return QColor(c)
            
            self.colors = [load_color(c) for c in palette_data.get("colors", [])]
            self.current_index = palette_data.get("current_index", 0)
            
            # Validate colors (remove invalid ones except transparent)
            def is_valid_color(c):
                if c == Qt.transparent:
                    return True
                return hasattr(c, 'isValid') and c.isValid()
            
            self.colors = [c for c in self.colors if is_valid_color(c)]
            
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    def get_all_colors(self):
        """Return all colors in the palette"""
        return list(self.colors)
