# PixelSmart Model Documentation

This document specifies the AI models required for PixelSmart, their expected APIs, alternative model options, hosting requirements, and implementation guidelines.

---

## Table of Contents

1. [Overview](#overview)
2. [Required Models](#required-models)
3. [Model APIs](#model-apis)
4. [Alternative Model Options](#alternative-model-options)
5. [Hosting Requirements](#hosting-requirements)
6. [Configuration](#configuration)
7. [Implementation Guidelines](#implementation-guidelines)

---

## Overview

PixelSmart requires three categories of AI models to support its creative workflow:

| Model Category | Purpose | Typical Use Cases |
|----------------|---------|-------------------|
| **Vision Model** | Analyze images, extract style information, generate descriptions | Style analysis, subject understanding |
| **Generation Model** | Create new pixel art from prompts and base images | Icon generation, style transfer |
| **Segmentation Model** | Detect foreground/background separation | Background removal, transparency creation |

All models are accessed via REST API endpoints (default: LM Studio) with fallback options for local inference.

---

## Required Models

### 1. Vision Model
**Purpose**: Analyze uploaded images to extract:
- Style description/prompt text
- Dominant color palette
- Artistic characteristics (pixel size, color count, texture)

**Key Inputs**:
- Image file path or base64-encoded image data
- Optional: Target resolution for analysis

**Key Outputs**:
```json
{
  "description": "8-bit style pixel art with vibrant colors and simple shapes",
  "palette": ["#FF0000", "#00FF00", "#0000FF", ...],
  "characteristics": {
    "pixel_size": 8,
    "color_count": 16,
    "style_tags": ["retro", "vibrant", "minimal"]
  }
}
```

### 2. Generation Model
**Purpose**: Generate pixel art images from text prompts and optionally base images

**Key Inputs**:
- Text prompt describing desired output
- Optional: Base image for style transfer or upscaling
- Optional: Target resolution (64x64 to 512x512)
- Optional: Style strength parameter (0.0 to 1.0)

**Key Outputs**:
- Generated pixel art image as PIL Image object or base64-encoded PNG

### 3. Segmentation Model
**Purpose**: Detect foreground objects and create transparency masks

**Key Inputs**:
- Input image with potential background pixels
- Optional: Confidence threshold for segmentation

**Key Outputs**:
- Binary mask (0 = background, 255 = foreground)
- Alpha channel data for transparency application

---

## Model APIs

### VisionModel Interface

```python
class VisionModel:
    async def analyze_style(self, image_path: str) -> dict:
        """
        Analyze a style image and return extraction results.
        
        Args:
            image_path: Path to the style image file
            
        Returns:
            {
                "description": str,           # Text description for generation
                "palette": List[str],         # Hex color codes
                "characteristics": dict       # Additional metadata
            }
        """
    
    async def analyze_subject(self, image_path: str) -> dict:
        """
        Analyze a subject image to understand its content.
        
        Args:
            image_path: Path to the subject image file
            
        Returns:
            {
                "description": str,
                "subject_area": [x, y, width, height],  # Bounding box
                "complexity_score": float               # 0.0-1.0
            }
        ```
```

### GenerationModel Interface

```python
class GenerationModel:
    async def generate(self, 
                      prompt: str, 
                      base_image_path: Optional[str] = None,
                      target_size: Tuple[int, int] = (64, 64),
                      style_strength: float = 0.7) -> Image:
        """
        Generate a pixel art image.
        
        Args:
            prompt: Text description for the generation
            base_image_path: Optional path to base image for style transfer
            target_size: Output dimensions (width, height)
            style_strength: How strongly to apply base image style (0.0-1.0)
            
        Returns:
            PIL Image object with generated pixel art
            
        Raises:
            GenerationError: If generation fails
        """
    
    async def upscale(self, 
                     image_path: str, 
                     target_size: Tuple[int, int]) -> Image:
        """
        Upscale an existing image while preserving pixel art style.
        
        Args:
            image_path: Path to source image
            target_size: Desired output dimensions
            
        Returns:
            Upscaled PIL Image object
        """
```

### SegmentationModel Interface

```python
class SegmentationModel:
    async def segment(self, 
                     image_path: str,
                     confidence_threshold: float = 0.5) -> np.ndarray:
        """
        Generate a foreground mask for an image.
        
        Args:
            image_path: Path to input image
            confidence_threshold: Minimum confidence for foreground classification
            
        Returns:
            Binary numpy array (height, width) with values 0 or 255
        ```
    
    async def apply_transparency(self, 
                                image_path: str,
                                mask: np.ndarray) -> Image:
        """
        Apply a segmentation mask to create transparency.
        
        Args:
            image_path: Path to source image
            mask: Binary mask array from segment() method
            
        Returns:
            PIL Image with alpha channel applied
        ```
```

---

## Alternative Model Options

### Vision Models

| Model | Strengths | Weaknesses | Hosting |
|-------|-----------|------------|---------|
| **Qwen-VL** | Strong multimodal understanding, good at style description | Larger model size (~8GB) | LM Studio, Ollama |
| **Gemma-Vision** | Lightweight, fast inference | Less detailed descriptions | LM Studio, Ollama |
| **LLaVA** | Good general-purpose vision language | Requires fine-tuning for pixel art | LM Studio, Ollama |
| **OpenAI GPT-4V** | Excellent descriptions, reliable | API costs, requires internet | Cloud API |

### Generation Models

| Model | Strengths | Weaknesses | Hosting |
|-------|-----------|------------|---------|
| **Stable Diffusion XL Base + ControlNet** | High quality, pixel-perfect control | Large (~7GB), slower generation | LM Studio, local PyTorch |
| **Stable Diffusion XL Turbo** | Fast generation, good quality | Less detailed than base | LM Studio, local PyTorch |
| **PixelArt-Specific SD Models** | Trained specifically on pixel art | Limited variety of styles | Custom hosting |
| **DALL-E 3 / Midjourney** | Excellent quality, easy to use | API costs, no local control | Cloud API |

### Segmentation Models

| Model | Strengths | Weaknesses | Hosting |
|-------|-----------|------------|---------|
| **SAM (Segment Anything)** | Highly accurate, flexible | Large (~400MB), slower | LM Studio, local PyTorch |
| **MobileSAM** | Lightweight, fast | Less accurate on complex images | LM Studio, local PyTorch |
| **U²-Net** | Good for foreground extraction | Requires training data | Local PyTorch |
| **BackgroundRemoval API** | Easy integration, reliable | API costs | Cloud API |

---

## Hosting Requirements

### Default: LM Studio (Recommended)

**Configuration**:
```json
{
  "api_endpoint": "http://localhost:1234/v1",
  "vision_model": "qwen-vl",
  "generation_model": "sdxl-base",
  "segmentation_model": "sam"
}
```

**Setup Steps**:
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Open LM Studio and navigate to the Model Catalog
3. Search for and download required models:
   - Vision: `qwen-vl` or `gemma-vision`
   - Generation: `sdxl-base` with ControlNet extension, or `sdxl-turbo`
   - Segmentation: `sam` or `mobile-sam`
4. Start the local server (default port 1234)
5. Configure PixelSmart to use `http://localhost:1234/v1`

**Advantages**:
- Free and open source
- No API costs
- Runs entirely locally
- Easy model switching via UI

### Alternative: Ollama

**Configuration**:
```json
{
  "api_endpoint": "http://localhost:11434",
  "vision_model": "gemma-vision",
  "generation_model": "stable-diffusion-xl-base",
  "segmentation_model": "mobile-sam"
}
```

**Setup Steps**:
1. Install [Ollama](https://ollama.com/)
2. Pull required models: `ollama pull gemma-vl`, etc.
3. Configure PixelSmart to use Ollama endpoint

### Alternative: Local PyTorch/ONNX Runtime

For advanced users who want maximum control:

**Requirements**:
- Python 3.10+ with PyTorch or ONNX Runtime
- Model files in appropriate format (.pt, .pth, .onnx)
- GPU recommended for reasonable performance

**Example Setup**:
```python
# Load model directly
from transformers import AutoModelForVision2Seq
model = AutoModelForVision2Seq.from_pretrained("qwen-vl")
```

### Alternative: Cloud APIs (Development Only)

For development without local models:

| Service | Endpoint | Cost |
|---------|----------|------|
| OpenAI GPT-4V | `https://api.openai.com/v1/chat/completions` | Per-image pricing |
| Replicate API | `https://api.replicate.com/v1` | Free tier available |
| Hugging Face Inference API | `https://api-inference.huggingface.co/v1` | Rate-limited free tier |

**Configuration Example**:
```json
{
  "api_endpoint": "https://api.openai.com/v1",
  "vision_model": "gpt-4v",
  "generation_model": "dall-e-3",
  "segmentation_model": "sam-v1"
}
```

---

## Configuration

### models.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["api_endpoint", "vision_model", "generation_model"],
  "properties": {
    "api_endpoint": {
      "type": "string",
      "description": "Base URL for model API endpoint",
      "default": "http://localhost:1234/v1"
    },
    "vision_model": {
      "type": "string",
      "description": "Name of vision model to use",
      "examples": ["qwen-vl", "gemma-vision"]
    },
    "generation_model": {
      "type": "string",
      "description": "Name of generation model to use",
      "examples": ["sdxl-base", "sdxl-turbo"]
    },
    "segmentation_model": {
      "type": "string",
      "description": "Name of segmentation model to use (optional)",
      "default": "sam"
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 300,
      "default": 60,
      "description": "Maximum time to wait for model responses"
    }
  }
}
```

### Default Configuration File

```json
{
  "api_endpoint": "http://localhost:1234/v1",
  "vision_model": "qwen-vl",
  "generation_model": "sdxl-base",
  "segmentation_model": "sam",
  "timeout_seconds": 60
}
```

---

## Implementation Guidelines

### Error Handling

All model operations must handle these error cases:

```python
try:
    result = await vision_model.analyze_style(image_path)
except NetworkError as e:
    show_error_dialog("Cannot connect to AI model server. Please ensure LM Studio is running.")
except ModelNotFoundError as e:
    show_error_dialog(f"Model '{model_name}' not found. Install it in LM Studio.")
except GenerationTimeoutError as e:
    show_error_dialog("AI generation timed out. Try a simpler prompt or larger timeout setting.")
```

### Progress Reporting

Long-running operations should report progress:

```python
async def generate_with_progress(prompt: str, callback):
    async for progress in generation_model.generate_stream(prompt):
        callback(progress)  # Update progress bar UI
```

### Model Swapping

The system must support runtime model switching without restart:

1. Load model configuration from `models.json`
2. Instantiate appropriate model class based on configuration
3. Cache model instances to avoid reloading
4. Allow user to change models via Settings dialog

### Performance Considerations

| Operation | Expected Time | Optimization |
|-----------|---------------|--------------|
| Style analysis | < 5 seconds | Use smaller vision models for quick previews |
| Icon generation (64x64) | 10-30 seconds | Use Turbo variants, reduce resolution |
| Background removal | 5-15 seconds | Cache masks, use MobileSAM for speed |

### Testing Strategy

1. **Unit Tests**: Mock model responses to test UI flow
2. **Integration Tests**: Test with real LM Studio endpoints
3. **Model Compatibility Tests**: Verify all three model categories work together
4. **Performance Tests**: Ensure operations complete within timeout limits

---

## Appendix: Model Selection Matrix

| Use Case | Recommended Vision Model | Recommended Generation Model |
|----------|-------------------------|------------------------------|
| Quick prototyping | Gemma-Vision | SDXL-Turbo |
| High-quality icons | Qwen-VL | SDXL-Base + ControlNet |
| Limited hardware | Gemma-Vision | MobileSD (if available) |
| Development/testing | Any (with mock fallback) | Any (with mock fallback) |

---

*Last updated: PixelSmart v0.1.0*
