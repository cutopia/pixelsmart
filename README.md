# PixelSmart

AI-powered pixel art editor for Ubuntu Linux.

## Features

### Phase 1 (Current - Complete):
- **Canvas Editor**: Grid-based drawing with zoom/pan capabilities
- **Drawing Tools**:
  - Pencil: Place individual pixels
  - Eraser: Remove pixels (set to transparent)
  - Bucket Fill: Flood fill an area with a color
  - Color Picker: Sample colors from the canvas
- **Palette Management**: Pre-defined palette with custom colors support
- **File I/O**: Save/load projects in `.pxsmart` format (ZIP-based)
- **PNG Export**: Export your artwork as PNG images

### Phase 2 (Current - AI Integration):
- **Style Transfer System**: Create pixel art icons by combining style and subject images
  - Upload style image for artistic inspiration
  - Upload subject image to transform
  - Generate pixel art icon in the desired style
  - Palette extraction from style images
  - Palette locking to preserve current colors
- **Background Remover**: Auto-detect and remove backgrounds to create transparency
- **AI Pixelizer**: Convert high-res images to pixel art (API-ready)

### Phase 3 (Planned):
- Animation timeline with onion skinning
- Layer management system
- Frame-by-frame animation editor

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pixelsmart

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Optional: AI Model Setup (for Style Transfer)

To use AI-powered features, you need to set up local AI models:

1. **Install LM Studio** (recommended):
   ```bash
   # Download from https://lmstudio.ai/
   ```

2. **Download Models** in LM Studio:
   - Vision model: `qwen-vl` or `gemma-vision`
   - Generation model: `sdxl-base` with ControlNet extension, or `sdxl-turbo`
   - Segmentation model: `sam` or `mobile-sam`

3. **Start LM Studio Server** (default port 1234)

For development without AI models, the application works in heuristic mode.

## Usage

```bash
# Run PixelSmart
python3 src/pixelsmart/main.py
```

### Keyboard Shortcuts:
- `B` / `P`: Pencil tool
- `E`: Eraser tool  
- `F`: Fill tool
- `I`: Picker tool
- `Ctrl+S`: Save project
- `Ctrl+O`: Open project

### Style Transfer Workflow:

1. **Upload Style Image**: Click "Upload Style Image..." in the AI Tools panel
   - System analyzes the style and extracts color palette
   - Palette is automatically applied (unless locked)

2. **Upload Subject Image**: Click "Upload Subject Image..."
   - Large images are sampled to target resolution

3. **Configure Generation**:
   - Adjust output resolution (default: 64x64)
   - Slide "Style Strength" to control how much style to apply
   - Check "Lock Current Palette" to preserve your palette

4. **Generate Icon**: Click "Generate Icon"
   - AI generates a pixel art icon in the desired style
   - Result appears on the canvas for manual refinement

5. **Refine & Export**: Edit the result manually, then save/export

### Background Removal:
- Select an image on the canvas
- Click "Background Remover" to remove edges and create transparency

## Project Structure

```
pixelsmart/
├── src/pixelsmart/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # Main application window
│   ├── canvas.py        # Canvas widget and drawing logic
│   ├── palette.py       # Palette management
│   ├── fileio.py        # Project file I/O
│   ├── ai_client.py     # AI API client (LM Studio, Ollama)
│   ├── style_analysis.py # Style image analysis & palette extraction
│   ├── subject_processor.py # Subject image sampling & preparation
│   ├── icon_generator.py  # AI-powered icon generation
│   └── background_remover.py # Background removal & transparency
├── tests/
│   ├── test_*.py        # Unit and integration tests
│   └── conftest.py      # Test fixtures
└── requirements.txt     # Python dependencies
```

## File Format

PixelSmart projects use the `.pxsmart` format, which is a ZIP archive containing:
- `manifest.json`: Canvas dimensions, zoom level, and metadata
- `canvas.png`: The actual pixel art image
- `palette.json`: (optional) Custom color palette

## AI Model Configuration

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

## License

MIT License - see LICENSE file for details.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pixelsmart

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run PixelSmart
python3 src/pixelsmart/main.py
```

### Keyboard Shortcuts:
- `B` / `P`: Pencil tool
- `E`: Eraser tool  
- `F`: Fill tool
- `I`: Picker tool
- `Ctrl+S`: Save project
- `Ctrl+O`: Open project

## Project Structure

```
pixelsmart/
├── src/pixelsmart/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # Main application window
│   ├── canvas.py        # Canvas widget and drawing logic
│   ├── palette.py       # Palette management
│   └── fileio.py        # Project file I/O
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## File Format

PixelSmart projects use the `.pxsmart` format, which is a ZIP archive containing:
- `manifest.json`: Canvas dimensions, zoom level, and metadata
- `canvas.png`: The actual pixel art image
- `palette.json`: (optional) Custom color palette

## License

MIT License - see LICENSE file for details.
