"""Style Analysis module for analyzing style images and extracting palettes."""

import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    from PySide6.QtGui import QImage
    HAS_QT = True
except ImportError:
    HAS_QT = False


class StyleAnalyzer:
    """
    Analyzes style images to extract artistic characteristics.
    
    Provides methods for analyzing pixel art style images and extracting:
    - Style description/prompt text
    - Dominant color palette
    - Artistic characteristics (pixel size, color count, texture)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the StyleAnalyzer.
        
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
    
    def analyze_style(
        self,
        image_path: str,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a style image and return extraction results.
        
        Args:
            image_path: Path to the style image file
            use_ai: If True, use AI model for analysis. If False, use heuristic methods.
            
        Returns:
            Dictionary with keys:
                - description: Text description of the style
                - palette: List of hex color codes
                - characteristics: Dict with pixel_size, color_count, style_tags
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if use_ai:
            return self._analyze_with_ai(image_path)
        else:
            return self._analyze_heuristic(image_path)
    
    def _analyze_with_ai(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze style using AI model.
        
        Args:
            image_path: Path to the style image
            
        Returns:
            Dictionary with analysis results
        """
        # TODO: Implement actual AI API call
        # For now, return mock data for testing
        return {
            "description": "8-bit style pixel art with vibrant colors and simple shapes",
            "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"],
            "characteristics": {
                "pixel_size": 8,
                "color_count": 16,
                "style_tags": ["retro", "vibrant", "minimal"]
            }
        }
    
    def _analyze_heuristic(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze style using heuristic methods (no AI required).
        
        Args:
            image_path: Path to the style image
            
        Returns:
            Dictionary with analysis results
        """
        if not HAS_QT:
            raise ImportError("PySide6 is required for heuristic analysis")
        
        # Load image
        image = QImage(image_path)
        if image.isNull():
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Extract colors from the image
        colors = self._extract_colors_heuristic(image)
        
        # Analyze characteristics
        characteristics = self._analyze_characteristics_heuristic(image, colors)
        
        return {
            "description": f"Pixel art style with {characteristics['color_count']} colors",
            "palette": colors,
            "characteristics": characteristics
        }
    
    def _extract_colors_heuristic(self, image: QImage) -> List[str]:
        """
        Extract dominant colors from an image using histogram analysis.
        
        Args:
            image: QImage to analyze
            
        Returns:
            List of hex color codes (up to 16 colors)
        """
        if not HAS_QT:
            return []
        
        # Sample pixels from the image
        width = image.width()
        height = image.height()
        
        # Use a grid sampling approach for efficiency
        sample_size = min(32, max(8, min(width, height) // 4))
        step_x = max(1, width // sample_size)
        step_y = max(1, height // sample_size)
        
        color_counts = {}
        
        for y in range(0, height, step_y):
            for x in range(0, width, step_x):
                pixel = image.pixel(x, y)
                # Convert to hex color
                color = f"#{pixel:08X}"  # ARGB format
                
                # Ignore fully transparent pixels
                alpha = (pixel >> 24) & 0xFF
                if alpha < 128:
                    continue
                
                # Count color occurrences
                color_counts[color] = color_counts.get(color, 0) + 1
        
        # Sort by frequency and take top colors
        sorted_colors = sorted(
            color_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return up to 16 most common colors
        return [color for color, count in sorted_colors[:16]]
    
    def _analyze_characteristics_heuristic(
        self,
        image: QImage,
        colors: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze artistic characteristics of the image.
        
        Args:
            image: QImage to analyze
            colors: List of extracted colors
            
        Returns:
            Dictionary with characteristic analysis
        """
        width = image.width()
        height = image.height()
        
        # Estimate pixel size based on image dimensions and color count
        # Smaller images with few colors suggest larger pixel sizes
        total_pixels = width * height
        
        if total_pixels < 1000:
            pixel_size = 32  # Very small, large pixels
        elif total_pixels < 10000:
            pixel_size = 16  # Small image
        elif total_pixels < 50000:
            pixel_size = 8  # Medium image
        else:
            pixel_size = 4  # Large image with small pixels
        
        return {
            "pixel_size": pixel_size,
            "color_count": len(colors),
            "style_tags": self._estimate_style_tags(width, height, colors)
        }
    
    def _estimate_style_tags(self, width: int, height: int, colors: List[str]) -> List[str]:
        """
        Estimate style tags based on image characteristics.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            colors: Extracted color palette
            
        Returns:
            List of style tag strings
        """
        tags = []
        
        # Analyze color count
        if len(colors) <= 8:
            tags.append("minimal")
        elif len(colors) <= 16:
            tags.append("limited")
        else:
            tags.append("vibrant")
        
        # Analyze size
        total_pixels = width * height
        if total_pixels < 1000:
            tags.append("micro")
        elif total_pixels < 10000:
            tags.append("small")
        elif total_pixels > 100000:
            tags.append("detailed")
        
        # Analyze color variety for style estimation
        if any(c.endswith("FF") and not c.startswith("#00") for c in colors[:4]):
            tags.append("bright")
        
        return tags
    
    def extract_palette(
        self,
        image_path: str,
        n_colors: int = 16,
        use_ai: bool = False
    ) -> List[str]:
        """
        Extract a color palette from a style image.
        
        Args:
            image_path: Path to the style image
            n_colors: Number of colors to extract (max)
            use_ai: If True, use AI model for analysis
            
        Returns:
            List of hex color codes
        """
        result = self.analyze_style(image_path, use_ai=use_ai)
        return result["palette"][:n_colors]
    
    def generate_style_prompt(
        self,
        image_path: str,
        use_ai: bool = True
    ) -> str:
        """
        Generate a text prompt describing the style of an image.
        
        Args:
            image_path: Path to the style image
            use_ai: If True, use AI model for analysis
            
        Returns:
            Text prompt describing the style
        """
        result = self.analyze_style(image_path, use_ai=use_ai)
        return result["description"]


def analyze_style_image(
    image_path: str,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze a style image.
    
    Args:
        image_path: Path to the style image
        config_path: Path to models.json configuration
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = StyleAnalyzer(config_path)
    return analyzer.analyze_style(image_path)


def extract_palette_from_image(
    image_path: str,
    n_colors: int = 16,
    config_path: Optional[str] = None
) -> List[str]:
    """
    Convenience function to extract a color palette from an image.
    
    Args:
        image_path: Path to the style image
        n_colors: Number of colors to extract (max)
        config_path: Path to models.json configuration
        
    Returns:
        List of hex color codes
    """
    analyzer = StyleAnalyzer(config_path)
    return analyzer.extract_palette(image_path, n_colors)
