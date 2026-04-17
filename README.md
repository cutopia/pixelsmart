# PixelSmart

AI-powered pixel art editor for Ubuntu Linux.

## Features

### Phase 1 (Current):
- **Canvas Editor**: Grid-based drawing with zoom/pan capabilities
- **Drawing Tools**:
  - Pencil: Place individual pixels
  - Eraser: Remove pixels (set to transparent)
  - Bucket Fill: Flood fill an area with a color
  - Color Picker: Sample colors from the canvas
- **Palette Management**: Pre-defined palette with custom colors support
- **File I/O**: Save/load projects in `.pxsmart` format (ZIP-based)
- **PNG Export**: Export your artwork as PNG images

### Phase 2 (Planned):
- AI Pixelizer: Convert high-res images to pixel art
- Background Remover: Auto-detect and remove backgrounds
- Flexible AI generation with reference image support

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
