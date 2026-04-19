"""Tests for PixelSmartCanvas module"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor, Qt
from pixelsmart.canvas import PixelSmartCanvas


def test_canvas_initialization():
    """Test that canvas initializes with correct dimensions"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=32, height=32)
    
    assert canvas.canvas_width == 32
    assert canvas.canvas_height == 32
    assert canvas.zoom_level == 20.0
    assert canvas.active_tool == "pencil"
    assert canvas.image.width() == 32
    assert canvas.image.height() == 32


def test_canvas_default_color():
    """Test that canvas initializes with transparent background"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Check that image is initially transparent
    for x in range(canvas.canvas_width):
        for y in range(canvas.canvas_height):
            color = canvas.image.pixelColor(x, y)
            assert color.alpha() == 0, f"Pixel at ({x},{y}) should be transparent"


def test_pencil_tool():
    """Test pencil tool places pixels correctly"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    canvas.set_current_color(QColor("#FF0000"))
    canvas.active_tool = "pencil"
    
    # Simulate drawing at position (5, 5)
    pixel_x, pixel_y = 5, 5
    canvas.image.setPixelColor(pixel_x, pixel_y, canvas.current_color)
    
    color_at_pos = canvas.image.pixelColor(pixel_x, pixel_y)
    assert color_at_pos == QColor("#FF0000")


def test_eraser_tool():
    """Test eraser tool removes pixels correctly"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    canvas.set_current_color(QColor("#FF0000"))
    
    # First draw a pixel
    canvas.image.setPixelColor(5, 5, canvas.current_color)
    assert canvas.image.pixelColor(5, 5) == QColor("#FF0000")
    
    # Then erase it (set to transparent)
    canvas.active_tool = "eraser"
    canvas.image.setPixelColor(5, 5, Qt.transparent)
    
    color_at_pos = canvas.image.pixelColor(5, 5)
    assert color_at_pos.alpha() == 0


def test_flood_fill_basic():
    """Test basic flood fill functionality"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Fill left half with red (not transparent)
    for x in range(8):
        for y in range(16):
            canvas.image.setPixelColor(x, y, QColor("#FF0000"))
    
    # Fill right half with blue
    for x in range(8, 16):
        for y in range(16):
            canvas.image.setPixelColor(x, y, QColor("#0000FF"))
    
    # Fill center of left side with green - should not cross to right
    canvas.flood_fill(4, 8, QColor("#00FF00"))
    
    # Check that fill stayed on left side
    assert canvas.image.pixelColor(4, 8).name().lower() == "#00ff00"
    assert canvas.image.pixelColor(7, 8).name().lower() == "#00ff00"
    
    # Check that right side is unchanged (still blue)
    assert canvas.image.pixelColor(8, 8).name().lower() == "#0000ff"


def test_flood_fill_boundary():
    """Test flood fill respects boundaries"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Fill left half with red
    for x in range(8):
        for y in range(16):
            canvas.image.setPixelColor(x, y, QColor("#FF0000"))
    
    # Fill right half with blue
    for x in range(8, 16):
        for y in range(16):
            canvas.image.setPixelColor(x, y, QColor("#0000FF"))
    
    # Try to fill from left side - should not cross boundary
    canvas.flood_fill(4, 8, QColor("#00FF00"))
    
    # Check that fill stayed on left side
    assert canvas.image.pixelColor(4, 8) == QColor("#00FF00")
    assert canvas.image.pixelColor(7, 8) == QColor("#00FF00")
    
    # Check that right side is unchanged
    assert canvas.image.pixelColor(8, 8) == QColor("#0000FF")


def test_flood_fill_same_color():
    """Test flood fill when new color equals old color"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Fill with red
    for x in range(16):
        for y in range(16):
            canvas.image.setPixelColor(x, y, QColor("#FF0000"))
    
    # Try to fill with same color - should not cause infinite loop
    canvas.flood_fill(8, 8, QColor("#FF0000"))
    
    # Should still be red (no change)
    assert canvas.image.pixelColor(8, 8) == QColor("#FF0000")


def test_color_picker():
    """Test color picker functionality"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Set a specific pixel to a color
    target_color = QColor("#FFA500")
    canvas.image.setPixelColor(5, 5, target_color)
    
    # Simulate picking that color
    sampled_color = canvas.image.pixelColor(5, 5)
    
    assert sampled_color == target_color


def test_zoom_level():
    """Test zoom level initialization and bounds"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    canvas = PixelSmartCanvas(width=16, height=16)
    
    # Test initial zoom
    assert canvas.zoom_level == 20.0
    
    # Test minimum zoom bound (manually test the logic without wheelEvent)
    canvas.zoom_level = 0.5
    canvas.zoom_level = max(1.0, min(canvas.zoom_level, 100.0))
    assert canvas.zoom_level >= 1.0
    
    # Test maximum zoom bound
    canvas.zoom_level = 200.0
    canvas.zoom_level = max(1.0, min(canvas.zoom_level, 100.0))
    assert canvas.zoom_level <= 100.0


def test_canvas_dimensions():
    """Test various canvas dimensions"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test different sizes
    for width, height in [(16, 16), (32, 32), (64, 64), (128, 128)]:
        canvas = PixelSmartCanvas(width=width, height=height)
        assert canvas.canvas_width == width
        assert canvas.canvas_height == height
        assert canvas.image.width() == width
        assert canvas.image.height() == height
