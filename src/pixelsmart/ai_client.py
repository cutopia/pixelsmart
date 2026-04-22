"""AI Client module for interacting with AI model endpoints."""

import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from PySide6.QtCore import QUrl
    from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
    from PySide6.QtGui import QImage
    HAS_QT = True
except ImportError:
    HAS_QT = False


class AIError(Exception):
    """Base exception for AI-related errors."""
    pass


class NetworkError(AIError):
    """Network communication error."""
    pass


class ModelNotFoundError(AIError):
    """Requested model not found on server."""
    pass


class GenerationError(AIError):
    """AI generation failed."""
    pass


class TimeoutError(AIError):
    """Request timed out."""
    pass


class AIClient:
    """
    Client for interacting with AI model endpoints.
    
    Supports LM Studio, Ollama, and other compatible API endpoints.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AI client.
        
        Args:
            config_path: Path to models.json configuration file. 
                        Uses default if not specified.
        """
        self.config = self._load_config(config_path)
        self.api_endpoint = self.config.get("api_endpoint", "http://localhost:1234/v1")
        self.timeout_seconds = self.config.get("timeout_seconds", 60)
        
        # Network manager for async requests
        self.network_manager = QNetworkAccessManager() if HAS_QT else None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path is None:
            # Default to models.json in same directory
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "models.json"
            )
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                "api_endpoint": "http://localhost:1234/v1",
                "vision_model": "qwen-vl",
                "generation_model": "sdxl-base",
                "segmentation_model": "sam",
                "timeout_seconds": 60
            }
        except json.JSONDecodeError as e:
            raise AIError(f"Invalid configuration file: {e}")
    
    def check_connection(self) -> bool:
        """Check if the AI endpoint is reachable."""
        # For now, return True - actual connection check would require HTTP request
        # This can be implemented later with proper async support
        return True
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from the server.
        
        Returns:
            List of model names available on the server.
        """
        # This would make an API call to /models endpoint
        # For now, return configured models
        models = []
        if self.config.get("vision_model"):
            models.append(self.config["vision_model"])
        if self.config.get("generation_model"):
            models.append(self.config["generation_model"])
        if self.config.get("segmentation_model"):
            models.append(self.config["segmentation_model"])
        return models
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded image data
        """
        import base64
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
    
    def prepare_vision_payload(
        self,
        image_path: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare payload for vision model API call.
        
        Args:
            image_path: Path to the image to analyze
            prompt: Optional text prompt for guided analysis
            
        Returns:
            Dictionary containing the API request payload
        """
        payload = {
            "model": self.config.get("vision_model", "qwen-vl"),
            "messages": [
                {
                    "role": "user",
                    "content": []
                }
            ]
        }
        
        # Add image to content
        base64_image = self.encode_image_to_base64(image_path)
        payload["messages"][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
        
        # Add text prompt if provided
        if prompt:
            payload["messages"][0]["content"].append({
                "type": "text",
                "text": prompt
            })
        else:
            # Default prompt for style analysis
            payload["messages"][0]["content"].append({
                "type": "text",
                "text": "Analyze this image and describe its artistic style, color palette, and pixel art characteristics. Return a JSON object with: description (string), palette (list of hex colors), characteristics (object with pixel_size, color_count, style_tags)."
            })
        
        return payload
    
    def prepare_generation_payload(
        self,
        prompt: str,
        base_image_path: Optional[str] = None,
        target_size: tuple = (64, 64),
        style_strength: float = 0.7
    ) -> Dict[str, Any]:
        """
        Prepare payload for generation model API call.
        
        Args:
            prompt: Text description for the generation
            base_image_path: Optional path to base image for style transfer
            target_size: Output dimensions (width, height)
            style_strength: How strongly to apply base image style (0.0-1.0)
            
        Returns:
            Dictionary containing the API request payload
        """
        payload = {
            "model": self.config.get("generation_model", "sdxl-base"),
            "messages": [
                {
                    "role": "user",
                    "content": []
                }
            ]
        }
        
        # Add text prompt
        payload["messages"][0]["content"].append({
            "type": "text",
            "text": f"Generate a pixel art image: {prompt}. Output dimensions: {target_size[0]}x{target_size[1]}. Style strength: {style_strength}"
        })
        
        # Add base image if provided
        if base_image_path:
            base64_image = self.encode_image_to_base64(base_image_path)
            payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
        
        return payload
    
    def prepare_segmentation_payload(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        Prepare payload for segmentation model API call.
        
        Args:
            image_path: Path to the image to segment
            
        Returns:
            Dictionary containing the API request payload
        """
        payload = {
            "model": self.config.get("segmentation_model", "sam"),
            "messages": [
                {
                    "role": "user",
                    "content": []
                }
            ]
        }
        
        # Add image to content
        base64_image = self.encode_image_to_base64(image_path)
        payload["messages"][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
        
        # Add segmentation prompt
        payload["messages"][0]["content"].append({
            "type": "text",
            "text": "Generate a segmentation mask for the foreground object in this image. Return the mask as a binary array where 255 represents foreground and 0 represents background."
        })
        
        return payload


# Convenience functions for common operations
def analyze_style(image_path: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a style image and return extraction results.
    
    Args:
        image_path: Path to the style image file
        config_path: Path to models.json configuration
        
    Returns:
        Dictionary with description, palette, and characteristics
    """
    client = AIClient(config_path)
    payload = client.prepare_vision_payload(image_path)
    
    # TODO: Implement actual API call
    raise NotImplementedError("API call implementation pending")


def generate_icon(
    prompt: str,
    base_image_path: Optional[str] = None,
    target_size: tuple = (64, 64),
    style_strength: float = 0.7,
    config_path: Optional[str] = None
) -> QImage:
    """
    Generate a pixel art icon using AI.
    
    Args:
        prompt: Text description for the generation
        base_image_path: Optional path to base image for style transfer
        target_size: Output dimensions (width, height)
        style_strength: How strongly to apply base image style (0.0-1.0)
        config_path: Path to models.json configuration
        
    Returns:
        Generated QImage object
    """
    client = AIClient(config_path)
    payload = client.prepare_generation_payload(
        prompt, base_image_path, target_size, style_strength
    )
    
    # TODO: Implement actual API call
    raise NotImplementedError("API call implementation pending")


def remove_background(image_path: str, config_path: Optional[str] = None) -> QImage:
    """
    Remove background from an image to create transparency.
    
    Args:
        image_path: Path to the input image
        config_path: Path to models.json configuration
        
    Returns:
        QImage with alpha channel applied
    """
    client = AIClient(config_path)
    payload = client.prepare_segmentation_payload(image_path)
    
    # TODO: Implement actual API call
    raise NotImplementedError("API call implementation pending")
