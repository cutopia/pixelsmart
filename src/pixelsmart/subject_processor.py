"""Subject Processing module for preparing subject images for AI generation."""

import os
from typing import Optional, Tuple

try:
    from PySide6.QtGui import QImage
    HAS_QT = True
except ImportError:
    HAS_QT = False


class SubjectProcessor:
    """
    Processes subject images for style transfer and icon generation.
    
    Provides methods for:
    - Sampling large images to target resolution
    - Cropping and centering subjects
    - Preparing images for AI generation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the SubjectProcessor.
        
        Args:
            config_path: Path to models.json configuration file.
                        Uses default if not specified.
        """
        self.config_path = config_path
    
    def sample_subject(
        self,
        image_path: str,
        target_size: Tuple[int, int] = (64, 64),
        preserve_aspect_ratio: bool = True
    ) -> QImage:
        """
        Sample a subject image to the target resolution.
        
        Args:
            image_path: Path to the source image (can be large)
            target_size: Target dimensions (width, height)
            preserve_aspect_ratio: If True, maintain aspect ratio with padding
            
        Returns:
            Resampled QImage at target resolution
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not HAS_QT:
            raise ImportError("PySide6 is required for image processing")
        
        # Load source image
        source_image = QImage(image_path)
        if source_image.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        target_width, target_height = target_size
        
        if preserve_aspect_ratio:
            return self._sample_with_padding(source_image, target_width, target_height)
        else:
            return self._sample_stretch(source_image, target_width, target_height)
    
    def _sample_with_padding(
        self,
        source: QImage,
        target_width: int,
        target_height: int
    ) -> QImage:
        """
        Sample image with padding to maintain aspect ratio.
        
        Args:
            source: Source QImage
            target_width: Target width
            target_height: Target height
            
        Returns:
            QImage padded to exact target dimensions
        """
        source_width = source.width()
        source_height = source.height()
        
        # Calculate scaling factor
        scale_x = target_width / source_width
        scale_y = target_height / source_height
        scale = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(source_width * scale)
        new_height = int(source_height * scale)
        
        # Resize with nearest neighbor for pixel art style
        resized = source.scaled(
            new_width,
            new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        
        # Create canvas with target dimensions
        result = QImage(target_width, target_height, QImage.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)
        
        # Center the resized image on the canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        painter = QPainter(result)
        painter.drawImage(x_offset, y_offset, resized)
        painter.end()
        
        return result
    
    def _sample_stretch(
        self,
        source: QImage,
        target_width: int,
        target_height: int
    ) -> QImage:
        """
        Sample image by stretching to fit target dimensions.
        
        Args:
            source: Source QImage
            target_width: Target width
            target_height: Target height
            
        Returns:
            QImage stretched to exact target dimensions
        """
        # Use nearest neighbor for pixel art style
        return source.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
    
    def crop_to_subject(
        self,
        image_path: str,
        confidence_threshold: float = 0.5
    ) -> QImage:
        """
        Crop an image to focus on the main subject.
        
        This is a placeholder method that would use segmentation models
        in a full implementation. For now, it returns a centered crop.
        
        Args:
            image_path: Path to the source image
            confidence_threshold: Minimum confidence for subject detection
            
        Returns:
            Cropped QImage focused on the subject
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not HAS_QT:
            raise ImportError("PySide6 is required for image processing")
        
        # Load image
        image = QImage(image_path)
        if image.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        width = image.width()
        height = image.height()
        
        # Calculate crop region (center 80% of image)
        crop_margin_x = int(width * 0.1)
        crop_margin_y = int(height * 0.1)
        
        crop_rect = QRect(
            crop_margin_x,
            crop_margin_y,
            width - 2 * crop_margin_x,
            height - 2 * crop_margin_y
        )
        
        # Extract cropped region
        return image.copy(crop_rect)
    
    def prepare_for_generation(
        self,
        image_path: str,
        target_size: Tuple[int, int] = (64, 64),
        style_description: Optional[str] = None
    ) -> Tuple[QImage, str]:
        """
        Prepare a subject image for AI generation.
        
        Combines sampling and optional style prompt enhancement.
        
        Args:
            image_path: Path to the subject image
            target_size: Target dimensions (width, height)
            style_description: Optional style description to prepend to prompt
            
        Returns:
            Tuple of (processed_image, enhanced_prompt)
        """
        # Sample the subject
        processed = self.sample_subject(image_path, target_size)
        
        # Build enhanced prompt
        if style_description:
            prompt = f"{style_description}, based on this image"
        else:
            prompt = "Pixel art version of this image"
        
        return processed, prompt
    
    def resize_for_canvas(
        self,
        image: QImage,
        canvas_width: int,
        canvas_height: int
    ) -> QImage:
        """
        Resize an image to fit the PixelSmart canvas dimensions.
        
        Args:
            image: Source QImage
            canvas_width: Target canvas width
            canvas_height: Target canvas height
            
        Returns:
            Resized QImage
        """
        return self.sample_subject(
            image,  # Pass QImage path or handle differently
            (canvas_width, canvas_height),
            preserve_aspect_ratio=True
        )


# Import Qt classes if available
if HAS_QT:
    from PySide6.QtCore import Qt, QRect
    from PySide6.QtGui import QPainter
