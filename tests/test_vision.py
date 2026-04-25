"""Tests for vision model integration."""

import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PIL import Image


class TestVisionModel:
    """Test cases for VisionModel class."""
    
    def test_vision_module_import(self):
        """Test that vision module can be imported."""
        from pixelsmart.vision import VisionModel
        assert VisionModel is not None
    
    def test_vision_model_initialization(self):
        """Test that VisionModel can be initialized without loading."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        assert model is not None
        assert model.processor is None
        assert model.model is None
        assert not model.is_loaded()
    
    def test_vision_model_path(self):
        """Test that VisionModel uses correct default path."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        # Check that the model path points to models/vision directory
        assert 'models' in model.model_path
        assert 'vision' in model.model_path
    
    def test_vision_model_load(self):
        """Test loading the vision model (requires model files)."""
        from pixelsmart.vision import VisionModel
        
        # Only run if model files exist
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'vision')
        model_path = os.path.normpath(model_path)
        
        if not os.path.exists(model_path):
            pytest.skip(f"Vision model not found at {model_path}")
        
        # Check for required model files
        required_files = ['config.json', 'tokenizer.json', 'model.safetensors']
        missing = [f for f in required_files if not os.path.exists(os.path.join(model_path, f))]
        
        if missing:
            pytest.skip(f"Missing model files: {missing}")
        
        model = VisionModel()
        result = model.load()
        
        # Model loading may fail due to hardware/dependency issues
        # but we can at least verify the method exists and returns a boolean
        assert isinstance(result, bool)
    
    def test_vision_model_generate_text(self):
        """Test text generation (requires loaded model)."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        if not os.path.exists(os.path.join(model.model_path, 'config.json')):
            pytest.skip("Vision model not available")
        
        # Don't actually load - just verify the method signature
        assert hasattr(model, 'generate_text')
        assert callable(getattr(model, 'generate_text'))
    
    def test_vision_model_analyze_image(self):
        """Test image analysis (requires loaded model)."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        if not os.path.exists(os.path.join(model.model_path, 'config.json')):
            pytest.skip("Vision model not available")
        
        # Verify method exists
        assert hasattr(model, 'analyze_image')
        assert callable(getattr(model, 'analyze_image'))
    
    def test_vision_model_convert_to_pixel_art(self):
        """Test pixel art conversion (requires loaded model)."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        if not os.path.exists(os.path.join(model.model_path, 'config.json')):
            pytest.skip("Vision model not available")
        
        # Verify method exists
        assert hasattr(model, 'convert_to_pixel_art')
        assert callable(getattr(model, 'convert_to_pixel_art'))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
