# PixelSmart AI Modules Documentation

This document describes the AI-powered features in PixelSmart and how they work.

## Overview

PixelSmart includes several AI modules that enable powerful image transformation capabilities:

| Module | Purpose | Status |
|--------|---------|--------|
| `ai_client.py` | API client for LM Studio, Ollama, and compatible endpoints | ✅ Complete |
| `style_analysis.py` | Analyze style images and extract color palettes | ✅ Complete |
| `subject_processor.py` | Sample and prepare subject images for generation | ✅ Complete |
| `icon_generator.py` | Generate pixel art icons using AI models | ✅ Complete |
| `background_remover.py` | Remove backgrounds to create transparency | ✅ Complete |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UI Layer (main.py)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│   AI Client      │  │   Style          │
│   (ai_client.py) │  │   Analyzer       │
│                  │  │  (style_analysis)│
│ - LM Studio API  │  │                  │
│ - Ollama API     │  │ - Color extraction│
│ - Model config   │  │ - Style analysis  │
└──────────────────┘  └──────────────────┘
        ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Subject          │  │ Icon Generator   │
│ Processor        │  │ (icon_generator) │
│ (subject_proc.)  │  │                  │
│ - Resizing       │  │ - AI generation  │
│ - Cropping       │  │ - Palette mapping│
└──────────────────┘  └──────────────────┘
        ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Background       │  │                  │
│ Remover          │  │                  │
│ (bg_remover.py)  │  │                  │
│ - Mask generation│  │                  │
│ - Transparency   │  │                  │
└──────────────────┘  └──────────────────┘
```

## AI Client (`ai_client.py`)

The `AIClient` class provides a unified interface for interacting with AI model endpoints.

### Configuration

Models are configured in `src/pixelsmart/models.json`:

```json
{
  "api_endpoint": "http://localhost:1234/v1",
  "vision_model": "qwen-vl",
  "generation_model": "sdxl-base",
  "segmentation_model": "sam",
  "timeout_seconds": 60
}
```

### Supported Endpoints

- **LM Studio** (default): `http://localhost:1234/v1`
- **Ollama**: `http://localhost:11434`
- **Cloud APIs**: OpenAI, Replicate, Hugging Face (with appropriate configuration)

### Key Methods

```python
client = AIClient()

# Prepare vision model payload
payload = client.prepare_vision_payload("style_image.png")

# Prepare generation model payload  
payload = client.prepare_generation_payload(
    prompt="8-bit style pixel art",
    base_image_path="subject.png",
    target_size=(64, 64),
    style_strength=0.7
)

# Encode image to base64 for API transmission
base64_data = client.encode_image_to_base64("image.png")
```

## Style Analyzer (`style_analysis.py`)

Analyzes style images to extract artistic characteristics.

### Key Features

1. **Color Palette Extraction**: Identifies dominant colors in an image
2. **Style Description**: Generates text descriptions of artistic style
3. **Characteristics Analysis**: Detects pixel size, color count, and style tags

### Usage

```python
from pixelsmart.style_analysis import StyleAnalyzer

analyzer = StyleAnalyzer()

# Analyze a style image (with AI)
result = analyzer.analyze_style("style.png", use_ai=True)

# Or use heuristic methods (no AI required)
result = analyzer.analyze_style("style.png", use_ai=False)

# Extract just the palette
palette = analyzer.extract_palette("style.png", n_colors=16)

# Generate a style prompt
prompt = analyzer.generate_style_prompt("style.png")
```

### Output Format

```python
{
    "description": "8-bit style pixel art with vibrant colors",
    "palette": ["#FF0000", "#00FF00", "#0000FF"],
    "characteristics": {
        "pixel_size": 8,
        "color_count": 16,
        "style_tags": ["retro", "vibrant", "minimal"]
    }
}
```

## Subject Processor (`subject_processor.py`)

Prepares subject images for AI generation.

### Key Features

1. **Aspect Ratio Preservation**: Pads images to maintain proportions
2. **Nearest Neighbor Scaling**: Preserves pixel art style during resizing
3. **Subject Cropping**: Focuses on main subject in image

### Usage

```python
from pixelsmart.subject_processor import SubjectProcessor

processor = SubjectProcessor()

# Sample subject to target size (with padding)
result = processor.sample_subject(
    "subject.png",
    target_size=(64, 64),
    preserve_aspect_ratio=True
)

# Prepare for generation with style prompt
processed, prompt = processor.prepare_for_generation(
    "subject.png",
    target_size=(64, 64),
    style_description="8-bit pixel art"
)
```

## Icon Generator (`icon_generator.py`)

Generates pixel art icons using AI models.

### Key Features

1. **Text-to-Icon Generation**: Create icons from text prompts
2. **Style Transfer**: Apply base image style to generated output
3. **Palette Constraint**: Map colors to a specific palette

### Usage

```python
from pixelsmart.icon_generator import IconGenerator

generator = IconGenerator()

# Generate icon from prompt
icon = generator.generate_icon(
    prompt="8-bit pixel art cat with vibrant colors",
    target_size=(64, 64),
    style_strength=0.7
)

# Constrain to specific palette
painted_icon = generator.constrain_to_palette(icon, ["#FF0000", "#00FF00"])

# Upscale existing image while preserving pixel art style
upscaled = generator.upscale("small.png", (128, 128))
```

## Background Remover (`background_remover.py`)

Removes backgrounds to create transparency.

### Key Features

1. **Heuristic Edge Detection**: Removes image edges as background
2. **Mask Generation**: Creates alpha masks for transparency
3. **Foreground Preservation**: Keeps main subject intact

### Usage

```python
from pixelsmart.background_remover import BackgroundRemover

remover = BackgroundRemover()

# Remove background from image
result = remover.remove_background("image.png", confidence_threshold=0.5)

# Get just the mask
mask = remover.auto_mask_subject("image.png")

# Apply transparency to existing canvas
transparent = remover.apply_transparency("image.png")
```

## Integration with Main Application

The AI modules are integrated into `main.py` through the `MainWindow` class:

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # Initialize AI components
        self.style_analyzer = StyleAnalyzer()
        self.subject_processor = SubjectProcessor()
        self.icon_generator = IconGenerator()
        self.background_remover = BackgroundRemover()
        
        # UI elements for style transfer
        self.style_upload_btn.clicked.connect(self.upload_style_image)
        self.generate_btn.clicked.connect(self.generate_icon)
```

### Style Transfer Workflow

1. **Upload Style Image** → Analyzes and extracts palette
2. **Upload Subject Image** → Samples to target resolution  
3. **Configure Parameters** → Resolution, style strength, palette lock
4. **Generate Icon** → AI creates pixel art in desired style
5. **Refine on Canvas** → Manual editing possible after generation

## Testing

All AI modules have unit tests:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run only AI module tests
python3 -m pytest tests/test_ai_modules.py -v
```

## Development Notes

### Adding New Models

To add a new model to the configuration:

1. Update `models.json` with the new model name
2. The client automatically detects and uses it
3. No code changes required!

### Heuristic Mode

All AI modules work in "heuristic mode" without AI models:
- Style analysis uses color histogram methods
- Subject processing uses standard image resizing
- Icon generation creates placeholder patterns
- Background removal uses edge detection heuristics

This allows development and testing without local AI models.

## Future Enhancements

- [ ] Full LM Studio API integration for real AI generation
- [ ] Batch processing of multiple images
- [ ] Style transfer presets (8-bit, 16-bit, retro, modern)
- [ ] Custom model training support
- [ ] GPU acceleration options
- [ ] Progress callbacks for long-running operations
