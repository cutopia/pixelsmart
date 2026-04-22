"""Background Remover module for automatic background removal and transparency creation."""

import os
from typing import Optional, Tuple

try:
    from PySide6.QtGui import QImage
    HAS_QT = True
except ImportError:
    HAS_QT = False


class BackgroundRemover:
    """
    Removes backgrounds from images to create transparency.
    
    Provides methods for:
    - Automatic background detection and removal
    - Foreground mask generation
    - Alpha channel creation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the BackgroundRemover.
        
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
    
    def remove_background(
        self,
        image_path: str,
        confidence_threshold: float = 0.5
    ) -> QImage:
        """
        Remove the background from an image to create transparency.
        
        Args:
            image_path: Path to the input image
            confidence_threshold: Minimum confidence for foreground classification
            
        Returns:
            QImage with alpha channel applied (background transparent)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not HAS_QT:
            raise ImportError("PySide6 is required for image processing")
        
        # Load source image
        source = QImage(image_path)
        if source.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Generate mask
        mask = self._generate_mask(source, confidence_threshold)
        
        # Apply mask to create transparency
        return self._apply_mask(source, mask)
    
    def _generate_mask(
        self,
        image: QImage,
        confidence_threshold: float = 0.5
    ) -> 'QImage':
        """
        Generate a foreground mask for the image.
        
        This is a placeholder implementation using heuristic methods.
        In a full implementation, this would use segmentation models.
        
        Args:
            image: Source QImage
            confidence_threshold: Minimum confidence for foreground classification
            
        Returns:
            Binary mask QImage (white = foreground, black = background)
        """
        width = image.width()
        height = image.height()
        
        # Create mask image
        mask = QImage(width, height, QImage.Format_Grayscale8)
        mask.fill(255)  # Start with all foreground
        
        # Heuristic: Assume center region is foreground
        margin_x = int(width * 0.1)
        margin_y = int(height * 0.1)
        
        for y in range(height):
            for x in range(width):
                # Check if pixel is near edge (likely background)
                is_edge = (
                    x < margin_x or 
                    x >= width - margin_x or
                    y < margin_y or 
                    y >= height - margin_y
                )
                
                if is_edge:
                    mask.setPixel(x, y, 0)  # Background
        
        return mask
    
    def _apply_mask(
        self,
        source: QImage,
        mask: 'QImage'
    ) -> QImage:
        """
        Apply a mask to create transparency.
        
        Args:
            source: Source QImage with original colors
            mask: Binary mask (255 = foreground, 0 = background)
            
        Returns:
            QImage with alpha channel based on mask
        """
        width = source.width()
        height = source.height()
        
        result = QImage(width, height, QImage.Format_ARGB32)
        
        for y in range(height):
            for x in range(width):
                # Get mask value
                mask_value = mask.pixel(x, y) & 0xFF
                
                # Get source color
                pixel = source.pixel(x, y)
                
                # Calculate alpha based on mask
                alpha = int(mask_value * 255 / 255)  # Normalize to 0-255
                
                # Create new pixel with alpha
                result.setPixel(
                    x, y,
                    (alpha << 24) | (pixel & 0x00FFFFFF)
                )
        
        return result
    
    def auto_mask_subject(self, image_path: str) -> 'QImage':
        """
        Automatically create a mask for the subject foreground.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Binary mask QImage (255 = foreground, 0 = background)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not HAS_QT:
            raise ImportError("PySide6 is required for image processing")
        
        # Load image
        image = QImage(image_path)
        if image.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        return self._generate_mask(image)
    
    def apply_transparency(
        self,
        image_path: str,
        mask: Optional['QImage'] = None
    ) -> QImage:
        """
        Apply transparency to an image using a mask.
        
        Args:
            image_path: Path to the input image
            mask: Optional pre-computed mask. If None, generates one.
            
        Returns:
            QImage with transparency applied
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load source image
        source = QImage(image_path)
        if source.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Generate or use provided mask
        if mask is None:
            mask = self._generate_mask(source)
        
        return self._apply_mask(source, mask)


# Import Qt classes if available
if HAS_QT:
    from PySide6.QtCore import Qt
