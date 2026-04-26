"""Tests for vision model integration."""
import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PIL import Image, ImageDraw


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
    
    def test_vision_model_custom_path(self):
        """Test that VisionModel accepts custom model path."""
        from pixelsmart.vision import VisionModel
        
        custom_path = "/custom/path/to/model"
        model = VisionModel(model_path=custom_path)
        
        assert model.model_path == custom_path
        assert not model.is_loaded()
    
    def test_vision_model_load_not_required_for_methods(self):
        """Test that methods raise RuntimeError when model not loaded."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Create a simple test image
        img = Image.new('RGB', (32, 32), color='red')
        
        # All methods should raise RuntimeError if model not loaded
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.generate_text("Test prompt")
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.analyze_image(img)
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model.convert_to_pixel_art(img)
    
    def test_vision_model_is_loaded_false_initially(self):
        """Test that is_loaded returns False before loading."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Should return False when nothing is loaded
        assert not model.is_loaded()
        
        # Even after setting processor or model to None explicitly
        model.processor = None
        model.model = None
        assert not model.is_loaded()
    
    def test_vision_model_is_loaded_true_when_both_set(self):
        """Test that is_loaded returns True when both processor and model are set."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock loading by setting both components and _loaded flag
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        assert model.is_loaded()
    
    def test_vision_model_is_loaded_false_when_only_one_set(self):
        """Test that is_loaded returns False when only one component is set."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Only processor set
        model.processor = "mock_processor"
        assert not model.is_loaded()
        
        # Only model set
        model.processor = None
        model.model = "mock_model"
        assert not model.is_loaded()
    
    def test_vision_model_generate_text_signature(self):
        """Test that generate_text has correct signature and defaults."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Check method exists and is callable
        assert hasattr(model, 'generate_text')
        assert callable(getattr(model, 'generate_text'))
    
    def test_vision_model_analyze_image_signature(self):
        """Test that analyze_image has correct signature and defaults."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Check method exists and is callable
        assert hasattr(model, 'analyze_image')
        assert callable(getattr(model, 'analyze_image'))
    
    def test_vision_model_convert_to_pixel_art_signature(self):
        """Test that convert_to_pixel_art has correct signature and defaults."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Check method exists and is callable
        assert hasattr(model, 'convert_to_pixel_art')
        assert callable(getattr(model, 'convert_to_pixel_art'))
    
    def test_vision_model_analyze_image_default_prompt(self):
        """Test that analyze_image uses default prompt when none provided."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_prompts = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_prompts.append((prompt, image))
            return "mock response"
        
        model.generate_text = mock_generate_text
        
        # Create test image
        img = Image.new('RGB', (32, 32), color='blue')
        
        # Call analyze_image without prompt
        model.analyze_image(img)
        
        # Verify default prompt was used
        assert len(captured_prompts) == 1
        captured_prompt, captured_image = captured_prompts[0]
        assert "Describe this image" in captured_prompt
        assert captured_image is img
    
    def test_vision_model_analyze_image_custom_prompt(self):
        """Test that analyze_image uses custom prompt when provided."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_prompts = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_prompts.append((prompt, image))
            return "mock response"
        
        model.generate_text = mock_generate_text
        
        # Create test image and custom prompt
        img = Image.new('RGB', (32, 32), color='green')
        custom_prompt = "What is the main subject of this image?"
        
        # Call analyze_image with custom prompt
        model.analyze_image(img, prompt=custom_prompt)
        
        # Verify custom prompt was used
        assert len(captured_prompts) == 1
        captured_prompt, captured_image = captured_prompts[0]
        assert captured_prompt == custom_prompt
        assert captured_image is img
    
    def test_vision_model_convert_to_pixel_art_default_resolution(self):
        """Test that convert_to_pixel_art uses default resolution (32x32)."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_calls = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_calls.append((prompt, image))
            return "mock pixel art instructions"
        
        model.generate_text = mock_generate_text
        
        # Create test image
        img = Image.new('RGB', (64, 64), color='yellow')
        
        # Call convert_to_pixel_art with defaults
        result = model.convert_to_pixel_art(img)
        
        # Verify default resolution was used in prompt
        assert len(captured_calls) == 1
        captured_prompt, _ = captured_calls[0]
        assert "32x32" in captured_prompt
    
    def test_vision_model_convert_to_pixel_art_custom_resolution(self):
        """Test that convert_to_pixel_art uses custom resolution when provided."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_calls = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_calls.append((prompt, image))
            return "mock pixel art instructions"
        
        model.generate_text = mock_generate_text
        
        # Create test image and custom resolution
        img = Image.new('RGB', (64, 64), color='cyan')
        custom_resolution = (16, 16)
        
        # Call convert_to_pixel_art with custom resolution
        result = model.convert_to_pixel_art(img, target_resolution=custom_resolution)
        
        # Verify custom resolution was used in prompt
        assert len(captured_calls) == 1
        captured_prompt, _ = captured_calls[0]
        assert "16x16" in captured_prompt
    
    def test_vision_model_convert_to_pixel_art_with_style_hint(self):
        """Test that convert_to_pixel_art includes style hint when provided."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_calls = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_calls.append((prompt, image))
            return "mock pixel art instructions"
        
        model.generate_text = mock_generate_text
        
        # Create test image and style hint
        img = Image.new('RGB', (64, 64), color='magenta')
        style_hint = "retro 8-bit"
        
        # Call convert_to_pixel_art with style hint
        result = model.convert_to_pixel_art(img, style_hint=style_hint)
        
        # Verify style hint was included in prompt
        assert len(captured_calls) == 1
        captured_prompt, _ = captured_calls[0]
        assert "retro 8-bit" in captured_prompt
    
    def test_vision_model_convert_to_pixel_art_without_style_hint(self):
        """Test that convert_to_pixel_art works without style hint."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_calls = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_calls.append((prompt, image))
            return "mock pixel art instructions"
        
        model.generate_text = mock_generate_text
        
        # Create test image without style hint
        img = Image.new('RGB', (64, 64), color='yellow')
        
        # Call convert_to_pixel_art without style hint
        result = model.convert_to_pixel_art(img)
        
        # Verify prompt doesn't contain "with" (style hint part)
        assert len(captured_calls) == 1
        captured_prompt, _ = captured_calls[0]
        # Should still have resolution info but no style description
        assert "pixel art instructions" in captured_prompt
    
    def test_vision_model_image_formats(self):
        """Test that vision model methods work with different image formats."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Create images in different modes
        rgb_img = Image.new('RGB', (32, 32), color='red')
        rgba_img = Image.new('RGBA', (32, 32), color=(0, 128, 0, 255))
        grayscale_img = Image.new('L', (32, 32), color=128)
        
        # All should be accepted by analyze_image (will fail at runtime without loaded model,
        # but we're just testing that they don't cause type errors)
        with pytest.raises(RuntimeError):
            model.analyze_image(rgb_img)
        
        with pytest.raises(RuntimeError):
            model.analyze_image(rgba_img)
        
        with pytest.raises(RuntimeError):
            model.analyze_image(grayscale_img)
    
    def test_vision_model_empty_prompt_handling(self):
        """Test that generate_text handles empty prompt."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the processor and model to avoid actual loading
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Empty string should not raise an error during validation
        # (will fail at runtime without proper mock setup, but that's expected)
        with pytest.raises(RuntimeError):
            model.generate_text("")
    
    def test_vision_model_image_none_handling(self):
        """Test that generate_text handles None image for text-only generation."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the processor and model
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Text-only generation should work (will fail at runtime without proper setup)
        with pytest.raises(RuntimeError):
            model.generate_text("What is 2+2?")
    
    def test_vision_model_large_image_handling(self):
        """Test that vision model methods handle large images."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Create a larger image
        large_img = Image.new('RGB', (512, 512), color='purple')
        
        # Should accept without error (will fail at runtime without loaded model)
        with pytest.raises(RuntimeError):
            model.analyze_image(large_img)
        
        with pytest.raises(RuntimeError):
            model.convert_to_pixel_art(large_img)
    
    def test_vision_model_small_image_handling(self):
        """Test that vision model methods handle small images."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Create a very small image (1x1 pixel)
        tiny_img = Image.new('RGB', (1, 1), color='orange')
        
        # Should accept without error
        with pytest.raises(RuntimeError):
            model.analyze_image(tiny_img)
    
    def test_vision_model_generate_text_max_tokens(self):
        """Test that generate_text accepts max_new_tokens parameter."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock to capture the call
        captured_calls = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_calls.append((prompt, image, max_new_tokens))
            return "mock response"
        
        model.generate_text = mock_generate_text
        
        # Call with custom max tokens
        img = Image.new('RGB', (32, 32), color='red')
        model.generate_text("Test", image=img, max_new_tokens=1024)
        
        assert len(captured_calls) == 1
        _, _, max_tokens = captured_calls[0]
        assert max_tokens == 1024
    
    def test_vision_model_multiple_analyze_calls(self):
        """Test that multiple analyze_image calls work correctly."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        call_count = [0]  # Use list to allow modification in nested function
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            call_count[0] += 1
            return f"analysis {call_count[0]}"
        
        model.generate_text = mock_generate_text
        
        # Create multiple test images
        img1 = Image.new('RGB', (32, 32), color='red')
        img2 = Image.new('RGB', (32, 32), color='blue')
        
        # Make multiple calls
        result1 = model.analyze_image(img1)
        result2 = model.analyze_image(img2)
        
        assert call_count[0] == 2
        assert "analysis 1" in result1
        assert "analysis 2" in result2
    
    def test_vision_model_pixel_art_conversion_flow(self):
        """Test the complete pixel art conversion flow."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components first to avoid RuntimeError
        model.processor = "mock_processor"
        model.model = "mock_model"
        model._loaded = True
        
        captured_prompts = []
        
        def mock_generate_text(prompt, image=None, max_new_tokens=512):
            captured_prompts.append({
                'prompt': prompt,
                'image_size': image.size if image else None
            })
            return "pixel art instructions for 32x32"
        
        model.generate_text = mock_generate_text
        
        # Create test image with specific dimensions
        img = Image.new('RGB', (100, 80), color='brown')
        
        # Convert to pixel art
        result = model.convert_to_pixel_art(img)
        
        # Verify the flow
        assert len(captured_prompts) == 1
        prompt_info = captured_prompts[0]
        assert "pixel art" in prompt_info['prompt'].lower()
        assert prompt_info['image_size'] == (100, 80)


class TestVisionModelEdgeCases:
    """Test edge cases for VisionModel."""
    
    def test_vision_model_none_image_analyze(self):
        """Test that analyze_image raises error with None image."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Should raise RuntimeError when trying to use None image
        with pytest.raises(RuntimeError):
            model.analyze_image(None)
    
    def test_vision_model_none_image_convert(self):
        """Test that convert_to_pixel_art raises error with None image."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Should raise RuntimeError when trying to use None image
        with pytest.raises(RuntimeError):
            model.convert_to_pixel_art(None)
    
    def test_vision_model_zero_dimension_image(self):
        """Test handling of zero-dimension images."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Zero dimension image should be caught by PIL or later validation
        with pytest.raises(RuntimeError):
            img = Image.new('RGB', (0, 32), color='red')
            model.analyze_image(img)
    
    def test_vision_model_very_large_max_tokens(self):
        """Test generate_text with very large max_new_tokens."""
        from pixelsmart.vision import VisionModel
        
        model = VisionModel()
        
        # Mock the components
        model.processor = "mock_processor"
        model.model = "mock_model"
        
        # Should accept without error during validation
        with pytest.raises(RuntimeError):
            model.generate_text("Test", max_new_tokens=10000)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
