"""Vision model integration using Google Gemma 4E4B."""

import os
from typing import Optional, List, Dict, Any
from PIL import Image


class VisionModel:
    """Wrapper for Gemma 4E4B vision model."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the vision model.
        
        Args:
            model_path: Path to the local model directory. Defaults to models/vision/
        """
        if model_path is None:
            # Default path relative to this module
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, '..', '..', 'models', 'vision')
            model_path = os.path.normpath(model_path)
        
        self.model_path = model_path
        self.processor = None
        self.model = None
        self._loaded = False
    
    def load(self) -> bool:
        """
        Load the vision model and processor.
        
        Returns:
            True if loading succeeded, False otherwise
        """
        try:
            from transformers import AutoProcessor, AutoModelForCausalLM
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(self.model_path)
            
            # Determine device - prefer ROCm if available, fallback to CPU
            device = "cpu"
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                elif hasattr(torch, 'is_rocm') and torch.is_rocm:
                    device = "rocm"
            except ImportError:
                pass
            
            # Load model with specified device
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                dtype="auto",
                device_map=device if device != "cpu" else None
            )
            
            self._loaded = True
            return True
            
        except Exception as e:
            print(f"Failed to load vision model: {e}")
            self._loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._loaded and self.processor is not None and self.model is not None
    
    def generate_text(
        self, 
        prompt: str, 
        image: Optional[Image.Image] = None,
        max_new_tokens: int = 512
    ) -> str:
        """
        Generate text response from the model using instruction-style prompting.
        
        Gemma 4E4B is an instruction-following model that doesn't use chat templates.
        For vision tasks, include <|image|> at the start of the prompt to embed the image.
        
        Args:
            prompt: Instruction-style prompt for the model
            image: Optional PIL Image to include in the prompt
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text response (extracted from full output)
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Build prompt - Gemma 4E4B expects <|image|> token for vision tasks
        if image is not None:
            full_prompt = f"{self.processor.image_token}\n{prompt}"
        else:
            full_prompt = prompt
        
        # Process input with the prompt and optional image
        inputs = self.processor(text=full_prompt, images=image, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Store the decoded prompt text (what processor actually uses)
        # This is what we'll search for in the output
        input_ids = inputs["input_ids"][0]
        decoded_prompt_text = self.processor.decode(input_ids, skip_special_tokens=True)
        
        # Generate output with proper stopping tokens
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,  # Use greedy decoding for instruction-following
            eos_token_id=self.processor.tokenizer.eos_token_id,
            pad_token_id=self.processor.tokenizer.pad_token_id
        )
        
        # Decode the full output (includes prompt + response)
        full_output = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the new content after the prompt
        response = self._extract_response(full_output, decoded_prompt_text)
        
        return response
    
    def _extract_response(self, full_output: str, decoded_prompt: str) -> str:
        """
        Extract just the new content from the model's output.
        
        Gemma 4E4B repeats the prompt in its output followed by the response,
        then often starts repeating. We extract just the first response line.
        
        Args:
            full_output: The complete decoded output from the model
            decoded_prompt: The prompt as decoded by the processor (what appears in output)
            
        Returns:
            Just the newly generated response text
        """
        if not full_output or not decoded_prompt:
            return ""
        
        # Find where the decoded prompt starts in the output
        prompt_idx = full_output.find(decoded_prompt)
        
        if prompt_idx >= 0:
            # Prompt found, extract what comes after it
            response_start = prompt_idx + len(decoded_prompt)
            remaining = full_output[response_start:]
            
            # Split by newlines and get the first non-empty line
            lines = [line.strip() for line in remaining.split('\n') if line.strip()]
            
            if lines:
                return lines[0]
            
            return ""
        
        # Fallback: return empty string (shouldn't happen normally)
        return ""
    
    def analyze_image(
        self, 
        image: Image.Image, 
        prompt: str = "Describe this image."
    ) -> str:
        """
        Analyze an image using the vision model.
        
        Args:
            image: PIL Image to analyze
            prompt: Prompt for analyzing the image
            
        Returns:
            Model's analysis of the image
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Use instruction-style prompting with image embedded
        # Note: generate_text will add <|image|> prefix when image is not None,
        # so we pass the prompt without it and let generate_text handle the token
        full_prompt = prompt
        return self.generate_text(full_prompt, image=image)
    
    def convert_to_pixel_art(
        self, 
        image: Image.Image,
        target_resolution: tuple = (32, 32),
        style_hint: str = ""
    ) -> str:
        """
        Convert an image to pixel art description.
        
        Args:
            image: Source PIL Image
            target_resolution: Target pixel art resolution (width, height)
            style_hint: Optional style guidance
            
        Returns:
            Pixel art generation instructions
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Use a simple instruction-style prompt for Gemma 4E4B
        # The model continues the prompt text, so we keep it short and direct
        style_desc = f' with {style_hint} style' if style_hint else ''
        prompt = f"Convert this image to pixel art{style_desc} at {target_resolution[0]}x{target_resolution[1]} resolution."
        
        return self.generate_text(prompt, image=image)
