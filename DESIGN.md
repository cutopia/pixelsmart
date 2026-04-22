# Software Design Specification: PixelSmart

## 1. Project Overview
PixelSmart is a Ubuntu-based pixel art drawing application that combines traditional manual pixel editing with AI-driven image transformation tools. The goal is to provide a professional workflow for game developers and artists to create high-quality pixel art assets.

## 2. Core Functional Requirements

### 2.1 Manual Pixel Editor
- **Canvas**: A grid-based drawing area with zoom/pan capabilities.
- **Tools**: 
    - Pencil (single pixel placement)
    - Eraser
    - Bucket Fill
    - Color Picker (eyedropper)
- **Palette Management**: Ability to create, save, and load custom color palettes.
- **Animation Support**: Frame-by-frame animation editor.
  - Import/export animated GIFs for team sharing
  - Export as PNG spritesheets for game engines
  - Onion skinning (rendering previous/next frames as overlays) - essential feature for first major update
- **Export**: Save as PNG with options to upscale without blurring (Nearest Neighbor).

### 2.2 AI-Driven Tooling

#### 2.2.1 Style Transfer System
The Style Transfer system enables users to create pixel art icons by combining a style image and subject image:

**Input Requirements:**
- **Style Image**: An image that demonstrates the desired artistic style (pixel art style, color palette, texture characteristics). Can be any resolution but typically high-resolution reference images work best.
- **Subject Image**: A large image containing the desired subject matter. The subject will be sampled/resized to the target icon size and transformed to match the style.

**Workflow:**
1. User uploads a style image → System analyzes style and extracts color palette
2. User uploads a subject image (large, high-resolution) → System samples it to target resolution
3. AI generates an icon in the desired style using the sampled subject as base
4. Optional background removal creates transparency for the final icon
5. User can manually refine the result in the canvas editor

**Output:**
- Pixel art icon (typically 64x64, 128x128, or up to 512x512)
- Saved as `.pxsmart` project or exported as PNG with transparency support

#### 2.2.2 AI Pixelizer
- **Input**: Source PNG image (can be high-resolution reference).
- **Parameters**: Target resolution (e.g., 16x16, 32x32), styling/palette constraints.
- **Output**: A pixelated version of the input image converted into a PixelSmart project.

#### 2.2.3 AI Background Remover
- **Input**: Icon/Sprite image.
- **Action**: Automatically detect and remove background pixels to create transparency.
- **Integration**: Can be applied after style transfer generation or to existing canvas content.

#### 2.2.4 Flexible AI Generation & Transformation
- Support for high-resolution reference images (style or subject matter) to guide generative models.
- Integrated workflow allowing seamless transition between AI generation, manual refinement, and further AI transformations.

## 3. Technical Architecture

### 3.1 Target Platform
- **OS**: Ubuntu Linux
- **Runtime**: Python 3.10+
- **UI Framework**: PySide6 (Qt for Python)

### 3.2 Image Processing Stack
- **Core Manipulation**: Pillow (PIL) or OpenCV.
- **AI Integration**: 
    - Interface via REST API to specialized models (e.g., Stable Diffusion with ControlNet for pixel art, or custom GANs).
    - Local inference via ONNX Runtime or PyTorch if hardware allows.

### 3.3 Model Swapping Architecture
The system is designed for flexibility in AI model selection:

**Configuration**: Models are specified in `models.json` configuration file with:
- `vision_model`: Name of vision model (e.g., "qwen-vl", "gemma-vision")
- `generation_model`: Name of generation model (e.g., "sdxl-base", "sdxl-turbo")
- `segmentation_model`: Name of background removal model
- `api_endpoint`: LM Studio endpoint URL (default: http://localhost:1234/v1)

**Model Interface**: All models implement a common interface:
```python
class VisionModel:
    def analyze(self, image_path) -> dict:  # Returns style description and palette
    
class GenerationModel:
    def generate(self, prompt, base_image=None) -> Image:  # Returns generated image

class SegmentationModel:
    def segment(self, image) -> Mask:  # Returns foreground mask
```

**Adding New Models**: Simply add to `models.json` with appropriate endpoint configuration.

### 3.4 Data Model & Storage
- **Project Format**: `.pxsmart` files implemented as compressed ZIP archives containing:
    - `manifest.json`: Metadata, canvas dimensions, zoom level, palette information
    - `canvas.png`: The main pixel art image (single layer)
    - `palette.json`: Custom color palette (optional)
    - `frames/`: Animation frames directory (optional)
        - `frame_000.png`, `frame_001.png`, etc.
        - `frame_info.json`: Frame timing and metadata
- **State Management**: Simple delta-based undo system storing only changed pixel coordinates and their previous color values.

### 3.5 Palette Management
- **Palette Locking**: Users can toggle palette lock to preserve current palette or allow it to be updated from style analysis.
- When unlocked: Style image analysis extracts dominant colors and updates the active palette.
- When locked: The existing palette is preserved during style transfer operations.

## 4. UI/UX Design

### 4.1 Layout
- **Left Sidebar**: Toolset (Pencil, Eraser, etc.).
- **Right Sidebar**: AI Tools Panel & Palette Manager.
    - Style Transfer Section:
        - "Upload Style Image" button with preview thumbnail
        - "Palette Lock" checkbox (preserves current palette)
        - "Upload Subject Image" button with preview thumbnail
        - Output resolution selector (64x64, 128x128, 256x256, 512x512)
        - Style strength slider (0-100%)
        - "Generate Icon" button
        - AI-generated prompt display with edit capability
    - Palette Manager:
        - Color swatches grid
        - Lock icon indicator when palette is locked
- **Center**: Canvas with grid overlays.
- **Bottom**: Animation timeline (frames, play controls).

### 4.2 Interactions
- Keyboard shortcuts for tool switching (e.g., `B` for Brush, `E` for Eraser).
- Progress dialog with progress bar for long-running AI operations.
- Status messages: "Analyzing style...", "Sampling subject...", "Generating icon..."

## 5. Implementation Status

### Phase 1: The Foundation (Manual Editor) ✅ COMPLETE
- Implement basic canvas rendering and grid system.
- Implement core drawing tools (Pencil, Eraser, Fill).
- Implement Palette and File I/O.

**Status**: All features implemented and tested.

### Phase 2: AI Integration & Animation ✅ IN PROGRESS
- Develop the API wrapper for local AI services (LM Studio endpoints).
- Implement "AI Pixelizer" logic (Downsampling + Color quantization).
- Implement Background Removal tool.
- **Implement Style Transfer System**:
    - Style Analysis module (analyze style image, extract palette)
    - Subject Processing module (sample large images to target size)
    - Icon Generator module (AI generation with style prompting)
    - Background Remover integration
    - UI components for style transfer workflow

**Status**: Core AI modules implemented. API client ready for LM Studio integration.

### Phase 3: Animation & Polish
- Implement animation preview player (FPS control, looping).
- UI refinement and Ubuntu-specific optimization (GTK theme integration).
- Performance optimizations for large canvas editing.
- Advanced onion skinning options (number of frames, opacity).

## 6. Constraints & Considerations
- **Scaling**: Ensure that when exporting, pixels remain sharp (disable bilinear interpolation).
- **Latency**: AI operations should be asynchronous to prevent UI freezing; provide progress indicators.
- **Resolution**: Target output is typically small (64x64 to 128x128), so subject images can be large and sampled down.
- **Background Removal**: Use the path of least resistance - likely a segmentation model that works well for foreground extraction.
- **Model Flexibility**: Design should allow easy swapping between different vision models (Qwen, Gemma) and generation models (SDXL variants).
- **Palette Management**: Support both locked (preserve current palette) and unlocked (auto-extract from style) modes.
- **Local Hosting**: All models hosted locally via LM Studio REST API endpoints by default (`http://localhost:1234/v1`).

## 7. Style Transfer System Details

### 7.1 Module Structure
```
src/pixelsmart/
├── style_analysis.py      # Analyze style images, extract palettes
├── subject_processor.py   # Sample and prepare subject images
├── icon_generator.py      # AI generation of pixel art icons
├── background_remover.py  # Remove backgrounds from generated icons
└── models.json            # Configuration for model selection
```

### 7.2 Technical Implementation

**API Integration:**
- LM Studio REST API endpoint (default: `http://localhost:1234/v1`)
- Async HTTP requests for non-blocking UI during AI operations
- Progress callbacks for long-running generation tasks

**Model Interface:**
```python
class VisionModel:
    def analyze_style(self, image_path) -> dict:
        # Returns: {description: str, palette: list[Color], characteristics: dict}
    
class GenerationModel:
    def generate(self, prompt: str, base_image=None) -> Image:
        # Returns generated pixel art image
```

### 7.3 User Workflow
1. **Upload Style Image**: System analyzes and displays style description prompt
2. **Upload Subject Image**: Large image is sampled to target resolution
3. **Configure Generation**: Select resolution, adjust style strength
4. **Generate Icon**: AI creates pixel art icon in the specified style
5. **Optional Background Removal**: Create transparency for the icon
6. **Manual Refinement**: User can edit the result in the canvas
7. **Save/Export**: Save as `.pxsmart` project or export PNG

### 7.4 Palette Locking Behavior
- **Locked (checked)**: Current palette is preserved during style transfer operations
- **Unlocked (unchecked)**: Palette is updated from dominant colors in the style image analysis

## 8. Error Handling & Edge Cases

### AI Operation Failures
- Network errors to local model endpoints should be caught and displayed as user-friendly messages
- Failed generation attempts should allow retry without losing progress
- Model not found: Prompt user to start LM Studio or check configuration

### User Cancellation
- Long-running operations (AI generation, background removal) should support cancellation
- Cancelled operations should leave canvas in previous state

### File Format Compatibility
- `.pxsmart` files should be versioned to handle future format changes
- Graceful handling of loading older project formats with missing data

## 9. Testing Strategy

### Unit Tests
- Canvas rendering and drawing tools
- Palette management (add, remove, save/load)
- File I/O operations (.pxsmart format)

### Integration Tests
- AI API integration with real models via LM Studio
- Style transfer workflow end-to-end
- Background removal accuracy testing
- Animation export (GIF and spritesheet) verification

### Test Infrastructure
- Mock AI endpoints for development without local models
- Real model integration tests when models are available
- CI/CD pipeline with test coverage reporting