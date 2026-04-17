"""PixelSmart - AI-powered pixel art editor"""
__version__ = "0.1.0"

from .canvas import PixelSmartCanvas
from .palette import PaletteManager
from .fileio import ProjectIO

__all__ = ['PixelSmartCanvas', 'PaletteManager', 'ProjectIO']
