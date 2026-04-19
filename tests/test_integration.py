"""Integration tests for PixelSmart Phase 1"""
import sys
import os
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from pixelsmart.canvas import PixelSmartCanvas
from pixelsmart.palette import PaletteManager
from pixelsmart.fileio import ProjectIO


def test_complete_workflow():
    """Test a complete user workflow: create, draw, save, load"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Step 1: Create canvas and set up palette
    canvas = PixelSmartCanvas(width=32, height=32)
    palette = PaletteManager()
    io_manager = ProjectIO()
    
    # Step 2: Draw something
    canvas.set_current_color(QColor("#FF0000"))
    canvas.flood_fill(16, 16, QColor("#FF0000"))  # Fill center with red
    
    canvas.set_current_color(QColor("#0000FF"))
    canvas.image.setPixelColor(10, 10, QColor("#0000FF"))  # Draw blue pixel
    canvas.image.setPixelColor(20, 20, QColor("#0000FF"))  # Draw another blue pixel
    
    # Step 3: Save project
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "workflow_test.pxsmart")
        
        assert io_manager.save_project(canvas, filepath, palette) is True
        
        # Step 4: Load project
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["canvas_width"] == 32
        assert result["canvas_height"] == 32
        
        # Verify some pixels were preserved
        loaded_image = result["canvas_image"]
        assert loaded_image.pixelColor(16, 16) == QColor("#FF0000")
        
        # Step 5: Continue editing after load
        canvas2 = PixelSmartCanvas(width=result["canvas_width"], height=result["canvas_height"])
        canvas2.image = loaded_image.copy()
        
        canvas2.set_current_color(QColor("#00FF00"))
        canvas2.image.setPixelColor(15, 15, QColor("#00FF00"))  # Add green pixel
        
        assert canvas2.image.pixelColor(15, 15) == QColor("#00FF00")


def test_multiple_save_load_cycles():
    """Test multiple save/load cycles don't degrade data"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    io_manager = ProjectIO()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "cycles_test.pxsmart")
        
        # Initial canvas
        canvas = PixelSmartCanvas(width=16, height=16)
        canvas.set_current_color(QColor("#FF0000"))
        canvas.flood_fill(8, 8, QColor("#FF0000"))
        
        # First cycle
        io_manager.save_project(canvas, filepath)
        result1 = io_manager.load_project(filepath)
        assert result1["success"] is True
        
        # Second cycle (save loaded data again)
        canvas2 = PixelSmartCanvas(width=result1["canvas_width"], height=result1["canvas_height"])
        canvas2.image = result1["canvas_image"].copy()
        
        io_manager.save_project(canvas2, filepath)
        result2 = io_manager.load_project(filepath)
        assert result2["success"] is True
        
        # Third cycle
        canvas3 = PixelSmartCanvas(width=result2["canvas_width"], height=result2["canvas_height"])
        canvas3.image = result2["canvas_image"].copy()
        
        io_manager.save_project(canvas3, filepath)
        result3 = io_manager.load_project(filepath)
        assert result3["success"] is True
        
        # Verify data integrity after multiple cycles
        assert result3["canvas_width"] == 16
        assert result3["canvas_height"] == 16


def test_palette_persistence():
    """Test that custom palette persists through save/load"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    io_manager = ProjectIO()
    
    # Create custom palette
    palette = PaletteManager()
    original_colors = [
        QColor("#FF0000"),   # Red
        QColor("#00FF00"),   # Green  
        QColor("#0000FF"),   # Blue
        QColor("#FFFF00"),   # Yellow
    ]
    
    for color in original_colors:
        palette.add_color(color)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "palette_test.pxsmart")
        
        canvas = PixelSmartCanvas(width=16, height=16)
        
        # Save with custom palette
        io_manager.save_project(canvas, filepath, palette)
        
        # Load and verify palette
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["palette_manager"] is not None
        
        loaded_palette = result["palette_manager"]
        
        # Check that custom colors were saved
        assert len(loaded_palette.colors) >= len(palette.colors)


def test_canvas_state_preservation():
    """Test that canvas state (zoom, offset) is preserved"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    io_manager = ProjectIO()
    
    # Create canvas with custom state
    canvas = PixelSmartCanvas(width=32, height=32)
    canvas.zoom_level = 25.0
    canvas.offset.setX(100)
    canvas.offset.setY(50)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "state_test.pxsmart")
        
        # Save state
        io_manager.save_project(canvas, filepath)
        
        # Load and verify state
        result = io_manager.load_project(filepath)
        
        assert result["success"] is True
        assert result["zoom_level"] == 25.0
        assert result["offset_x"] == 100
        assert result["offset_y"] == 50
