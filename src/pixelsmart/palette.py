"""Palette management module for PixelSmart"""
import json
from PySide6.QtGui import QColor


class PaletteManager:
    """Manages color palettes for the pixel art editor"""
    
    def __init__(self):
        self.colors = [
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
            QColor("#FFFFFF")   # Light Gray
        ]
        self.current_index = 0
    
    def add_color(self, color):
        """Add a new color to the palette"""
        if isinstance(color, str):
            color = QColor(color)
        if color.isValid() and color not in self.colors:
            self.colors.append(color)
    
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
        return QColor("#000000")
    
    def set_current_color(self, index):
        """Set the current color by palette index"""
        if 0 <= index < len(self.colors):
            self.current_index = index
            return self.colors[index]
        return None
    
    def get_current_color(self):
        """Get the currently selected color"""
        return self.get_color(self.current_index)
    
    def set_current_color_obj(self, color):
        """Set current color to an exact match if exists, or add new"""
        if color in self.colors:
            self.current_index = self.colors.index(color)
        else:
            self.add_color(color)
            self.current_index = len(self.colors) - 1
    
    def save_to_file(self, filepath):
        """Save palette to a JSON file"""
        palette_data = {
            "colors": [color.name() for color in self.colors],
            "current_index": self.current_index
        }
        with open(filepath, 'w') as f:
            json.dump(palette_data, f, indent=2)
    
    def load_from_file(self, filepath):
        """Load palette from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                palette_data = json.load(f)
            
            self.colors = [QColor(c) for c in palette_data.get("colors", [])]
            self.current_index = palette_data.get("current_index", 0)
            
            # Validate colors
            self.colors = [c for c in self.colors if c.isValid()]
            
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    def get_all_colors(self):
        """Return all colors in the palette"""
        return list(self.colors)
