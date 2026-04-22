"""Icon Generator module for AI-powered pixel art generation."""

import os
from typing import Optional, List, Tuple

try:
    from PySide6.QtGui import QImage, QColor
    HAS_QT = True
except ImportError:
    HAS_QT = False


class IconGenerator:
    """
    Generates pixel art icons using AI models.
    
    Provides methods for:
    - Generating icons from text prompts
    - Style transfer with base images
    - Palette-constrained generation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the IconGenerator.
        
        Args:
            config_path: Path to models.json configuration file.
                        Uses default if not specified.
        """
        self.config_path = config_path
        self._ai_client = None
    
    @property
    def ai_client(self):
        """Lazy-load AI client."""
        if self._ai_client is None:
            from pixelsmart.ai_client import AIClient
            self._ai_client = AIClient(self.config_path)
        return self._ai_client
    
    def generate_icon(
        self,
        prompt: str,
        base_image_path: Optional[str] = None,
        target_size: Tuple[int, int] = (64, 64),
        style_strength: float = 0.7
    ) -> QImage:
        """
        Generate a pixel art icon using AI.
        
        Args:
            prompt: Text description for the generation
            base_image_path: Optional path to base image for style transfer
            target_size: Output dimensions (width, height)
            style_strength: How strongly to apply base image style (0.0-1.0)
            
        Returns:
            Generated QImage object
            
        Raises:
            GenerationError: If generation fails
        """
        if not HAS_QT:
            raise ImportError("PySide6 is required for image generation")
        
        # TODO: Implement actual AI API call
        # For now, return a mock pixel art icon
        
        width, height = target_size
        result = QImage(width, height, QImage.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)
        
        # Create a simple placeholder pattern (this would be replaced by AI generation)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # No AA for pixel art
        
        # Draw some pixel art-like shapes as placeholder
        if width >= 16 and height >= 16:
            # Simple face pattern
            painter.fillRect(0, 0, width, height, Qt.GlobalColor.cyan)
            
            # Eyes
            eye_size = max(2, width // 8)
            painter.fillRect(width // 4, height // 3, eye_size, eye_size, Qt.GlobalColor.black)
            painter.fillRect(3 * width // 4 - eye_size, height // 3, eye_size, eye_size, Qt.GlobalColor.black)
            
            # Mouth
            mouth_y = 2 * height // 3
            painter.fillRect(width // 4, mouth_y, width // 2, max(1, height // 16), Qt.GlobalColor.black)
        
        painter.end()
        
        return result
    
    def generate_with_palette(
        self,
        prompt: str,
        palette: List[str],
        target_size: Tuple[int, int] = (64, 64),
        style_strength: float = 0.7
    ) -> QImage:
        """
        Generate an icon constrained to a specific color palette.
        
        Args:
            prompt: Text description for the generation
            palette: List of hex color codes to constrain to
            target_size: Output dimensions (width, height)
            style_strength: How strongly to apply base image style (0.0-1.0)
            
        Returns:
            Generated QImage with colors from the palette
        """
        # Generate icon first
        icon = self.generate_icon(prompt, None, target_size, style_strength)
        
        # Apply palette constraint
        return self.constrain_to_palette(icon, palette)
    
    def constrain_to_palette(
        self,
        image: QImage,
        palette: List[str]
    ) -> QImage:
        """
        Map an image's colors to the closest colors in a palette.
        
        Args:
            image: Source QImage
            palette: List of hex color codes
            
        Returns:
            QImage with colors mapped to palette
        """
        if not HAS_QT:
            raise ImportError("PySide6 is required for color mapping")
        
        # Convert hex colors to QColor objects
        q_colors = []
        for hex_color in palette:
            if hex_color.startswith('#'):
                q_colors.append(QColor(hex_color))
            else:
                q_colors.append(QColor(f"#{hex_color}"))
        
        width = image.width()
        height = image.height()
        
        result = QImage(width, height, QImage.Format_ARGB32)
        
        for y in range(height):
            for x in range(width):
                pixel = image.pixel(x, y)
                
                # Get RGB values
                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF
                
                # Find closest color in palette
                closest_color = self._find_closest_color(r, g, b, q_colors)
                
                # Set the new pixel color
                result.setPixel(x, y, closest_color.rgba())
        
        return result
    
    def _find_closest_color(
        self,
        r: int,
        g: int,
        b: int,
        palette: List[QColor]
    ) -> QColor:
        """
        Find the closest color in palette to the given RGB values.
        
        Uses Euclidean distance in RGB space.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            palette: List of QColor objects
            
        Returns:
            Closest QColor from the palette
        """
        if not palette:
            return QColor(r, g, b)
        
        min_distance = float('inf')
        closest = palette[0]
        
        for color in palette:
            pr = color.red()
            pg = color.green()
            pb = color.blue()
            
            # Euclidean distance in RGB space
            distance = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            
            if distance < min_distance:
                min_distance = distance
                closest = color
        
        return closest
    
    def upscale(
        self,
        image_path: str,
        target_size: Tuple[int, int]
    ) -> QImage:
        """
        Upscale an existing pixel art image while preserving style.
        
        Args:
            image_path: Path to source image
            target_size: Desired output dimensions
            
        Returns:
            Upscaled QImage
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not HAS_QT:
            raise ImportError("PySide6 is required for image processing")
        
        # Load source image
        source = QImage(image_path)
        if source.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        target_width, target_height = target_size
        
        # Use nearest neighbor scaling to preserve pixel art style
        return source.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation  # Nearest neighbor
        )


# Import Qt classes if available
if HAS_QT:
    from PySide6.QtCore import Qt, QRect
    from PySide6.QtGui import QPainter, QColor
