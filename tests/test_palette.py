"""Tests for PaletteManager module"""
import sys
import os
import json
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtGui import QColor, Qt
from pixelsmart.palette import PaletteManager


def test_palette_initialization():
    """Test that palette initializes with correct number of colors"""
    manager = PaletteManager()
    
    # Should have 16 colors: 1 transparent + 15 default colors
    assert len(manager.colors) == 16
    assert manager.current_index == 1  # Start with black (index 1)
    
    # Check that slot 0 is always transparent
    assert manager.get_color(0) == Qt.transparent
    
    # Check some default colors
    assert manager.get_color(1) == QColor("#000000")  # Black
    assert manager.get_color(2) == QColor("#FFFFFF")  # White
    assert manager.get_color(3) == QColor("#FF0000")  # Red


def test_add_color():
    """Test adding new colors to palette"""
    manager = PaletteManager()
    
    initial_count = len(manager.colors)
    manager.add_color(QColor("#FFA500"))  # Orange
    
    assert len(manager.colors) == initial_count + 1
    assert manager.colors[-1] == QColor("#FFA500")


def test_add_duplicate_color():
    """Test that adding duplicate color doesn't increase count"""
    manager = PaletteManager()
    
    initial_count = len(manager.colors)
    manager.add_color(QColor("#000000"))  # Black already exists
    
    assert len(manager.colors) == initial_count


def test_set_current_index():
    """Test setting current color by index"""
    manager = PaletteManager()
    
    manager.set_current_index(3)  # Red
    assert manager.current_index == 3
    assert manager.get_current_color() == QColor("#FF0000")


def test_get_current_color():
    """Test getting current color"""
    manager = PaletteManager()
    
    initial_color = manager.get_current_color()
    assert initial_color == QColor("#000000")  # Black is default


def test_remove_color():
    """Test removing colors from palette"""
    manager = PaletteManager()
    
    initial_count = len(manager.colors)
    manager.add_color(QColor("#FFA500"))  # Add orange
    manager.remove_color(initial_count)  # Remove the one we just added
    
    assert len(manager.colors) == initial_count


def test_remove_minimum_enforcement():
    """Test that minimum color count is enforced"""
    manager = PaletteManager()
    
    # Try to remove colors until we hit the limit (16)
    while len(manager.colors) > 16:
        manager.remove_color(len(manager.colors) - 1)
    
    assert len(manager.colors) == 16
    
    # Should not be able to remove below minimum
    initial_count = len(manager.colors)
    manager.remove_color(initial_count - 1)
    
    assert len(manager.colors) == initial_count


def test_save_and_load_palette():
    """Test saving and loading palette from file"""
    manager = PaletteManager()
    
    # Modify the palette
    manager.add_color(QColor("#FFA500"))  # Orange
    manager.set_current_index(3)  # Red
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save
        manager.save_to_file(temp_path)
        
        # Verify file was created
        assert os.path.exists(temp_path)
        
        # Create new manager and load
        new_manager = PaletteManager()
        result = new_manager.load_from_file(temp_path)
        
        assert result is True
        assert len(new_manager.colors) == len(manager.colors)
        # Note: Qt.transparent gets converted to "#00000000" when saved/loaded
        loaded_color = new_manager.get_color(0)
        # Check if it's transparent (either Qt.transparent or a QColor with alpha=0)
        is_transparent = (loaded_color == Qt.transparent or 
                         (hasattr(loaded_color, 'alpha') and loaded_color.alpha() == 0))
        assert is_transparent, "First color should be transparent"
        
    finally:
        os.unlink(temp_path)


def test_load_invalid_palette():
    """Test loading from invalid file"""
    manager = PaletteManager()
    
    # Try to load from non-existent file
    result = manager.load_from_file("/nonexistent/path/palette.json")
    assert result is False
    
    # Try to load from invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json {")
        temp_path = f.name
    
    try:
        result = manager.load_from_file(temp_path)
        assert result is False
        
    finally:
        os.unlink(temp_path)


def test_get_all_colors():
    """Test getting all colors from palette"""
    manager = PaletteManager()
    
    colors = manager.get_all_colors()
    
    assert len(colors) == 16
    assert colors[0] == Qt.transparent
    assert colors[1] == QColor("#000000")


def test_set_current_color_obj():
    """Test setting current color by object match"""
    manager = PaletteManager()
    
    # Set to a color that exists
    manager.set_current_color_obj(QColor("#FF0000"))
    assert manager.current_index == 3
    
    # Add and set to a new color
    new_color = QColor("#FFA500")
    manager.set_current_color_obj(new_color)
    
    assert len(manager.colors) == 17  # 16 + 1 new
    assert manager.get_current_color() == new_color
