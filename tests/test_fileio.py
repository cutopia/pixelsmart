"""Tests for ProjectIO module"""
import sys
import os
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor
from pixelsmart.canvas import PixelSmartCanvas
from pixelsmart.palette import PaletteManager
from pixelsmart.fileio import ProjectIO


def test_save_project_basic():
    """Test basic project saving"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.pxsmart")
        
        result = io_manager.save_project(canvas, filepath)
        
        assert result is True
        assert os.path.exists(filepath)
        assert filepath.endswith('.pxsmart')


def test_save_project_with_palette():
    """Test saving project with palette"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    palette = PaletteManager()
    io_manager = ProjectIO()
    
    # Add a custom color to palette
    palette.add_color(QColor("#FFA500"))
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_with_palette.pxsmart")
        
        result = io_manager.save_project(canvas, filepath, palette)
        
        assert result is True
        assert os.path.exists(filepath)


def test_save_project_auto_extension():
    """Test that .pxsmart extension is added automatically"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test")  # No extension
        
        result = io_manager.save_project(canvas, filepath)
        
        assert result is True
        assert os.path.exists(filepath + '.pxsmart')


def test_load_project_basic():
    """Test basic project loading"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save first
        filepath = os.path.join(tmpdir, "test.pxsmart")
        io_manager.save_project(canvas, filepath)
        
        # Load back
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["canvas_width"] == 16
        assert result["canvas_height"] == 16


def test_load_project_with_palette():
    """Test loading project with saved palette"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    palette = PaletteManager()
    io_manager = ProjectIO()
    
    # Modify palette
    palette.add_color(QColor("#FFA500"))
    palette.set_current_index(3)  # Red
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_with_palette.pxsmart")
        
        # Save with palette
        io_manager.save_project(canvas, filepath, palette)
        
        # Load back
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["palette_manager"] is not None


def test_save_load_cycle():
    """Test complete save and load cycle preserves data"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create canvas with some drawing
    canvas = PixelSmartCanvas(width=16, height=16)
    canvas.set_current_color(QColor("#FF0000"))
    canvas.flood_fill(8, 8, QColor("#FF0000"))  # Fill center with red
    
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "cycle_test.pxsmart")
        
        # Save
        assert io_manager.save_project(canvas, filepath) is True
        
        # Load
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["canvas_width"] == 16
        assert result["canvas_height"] == 16
        assert isinstance(result["canvas_image"], QImage)


def test_load_nonexistent_file():
    """Test loading from non-existent file"""
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "nonexistent.pxsmart")
        
        result = io_manager.load_project(filepath)
        
        assert result["success"] is False


def test_last_loaded_path():
    """Test that last_loaded_path is updated"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.pxsmart")
        
        # Save and check path is updated
        io_manager.save_project(canvas, filepath)
        assert io_manager.last_loaded_path == filepath
        
        # Load and check path is updated
        io_manager.load_project(filepath)
        assert io_manager.last_loaded_path == filepath


def test_save_load_with_custom_dimensions():
    """Test saving and loading with non-standard dimensions"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=64, height=32)  # Non-square
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "custom_dims.pxsmart")
        
        # Save
        assert io_manager.save_project(canvas, filepath) is True
        
        # Load
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["canvas_width"] == 64
        assert result["canvas_height"] == 32
