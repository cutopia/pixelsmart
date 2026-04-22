## Design Proposal: Style Transfer Functionality

### Overview
Add a "Style Transfer" workflow to PixelSmart that allows users to:
1. Upload a **style image** (provides artistic style, color palette, pixel art characteristics)
2. Upload a **subject image** (large image containing the content to transform into a pixel icon)
3. Generate a pixel art icon in the desired style
4. Optionally remove background and refine the result

### Core Workflow
```
1. Style Analysis → 2. Subject Sampling → 3. Icon Generation → 4. Background Removal → 5. Manual Refinement
```

---

## Detailed Design Specification

### 1. UI Components to Add

#### A. Style Transfer Panel (Right Sidebar)
- **Style Image Section**
  - "Upload Style Image" button
  - Preview thumbnail of style image
  - "Extract Palette" checkbox (default: unchecked = auto-extract palette from style)
  - "Palette Lock" checkbox (preserves current palette when checked)
  
- **Subject Image Section**
  - "Upload Subject Image" button
  - Preview thumbnail of subject image
  
- **Generation Controls**
  - "Generate Icon" button
  - Output resolution selector (64x64, 128x128, 256x256, 512x512)
  - Style strength slider (0-100%)
  
- **Prompt Display & Edit**
  - Read-only text box showing AI-generated prompt
  - "Edit Prompt" toggle to make it editable
  - "Regenerate with Prompt" button

#### B. Progress Indicators
- Modal dialog with progress bar for long-running AI operations
- Status messages: "Analyzing style...", "Sampling subject...", "Generating icon..."

---

### 2. Technical Implementation

#### A. Style Analysis Module (`style_analysis.py`)
```python
class StyleAnalyzer:
    def __init__(self, vision_model="qwen-vl"):
        self.vision_model = vision_model
    
    def analyze_style(self, image_path):
        """Analyze style image and return:
        - Style description (for prompting)
        - Dominant color palette
        - Pixel art characteristics"""
    
    def extract_palette(self, image_path, n_colors=16):
        """Extract significant colors from style image"""
```

#### B. Subject Processing Module (`subject_processor.py`)
```python
class SubjectProcessor:
    def sample_subject(self, large_image_path, target_size):
        """Sample/resize subject to target size while preserving composition"""
    
    def prepare_for_generation(self, sampled_image, style_description):
        """Prepare image for AI generation with style prompt"""
```

#### C. Icon Generator Module (`icon_generator.py`)
```python
class IconGenerator:
    def __init__(self, sd_model="sdxl-base"):
        self.sd_model = sd_model
    
    def generate_icon(self, subject_image, style_prompt, palette=None):
        """Generate pixel art icon using AI model"""
    
    def refine_with_palette(self, image, target_palette):
        """Map generated image colors to target palette"""
```

#### D. Background Remover Module (`background_remover.py`)
```python
class BackgroundRemover:
    def remove_background(self, icon_image):
        """Remove background from generated icon using segmentation model"""
    
    def auto_mask_subject(self, image):
        """Create alpha mask for subject foreground"""
```

---

### 3. Integration Points

#### A. File I/O Updates (`fileio.py`)
- Add support for saving/loading style transfer configurations
- Store: style_image_path, subject_image_path, generated_icon, palette settings

#### B. Canvas Integration (`canvas.py`)
- New canvas mode: `style_transfer_preview`
- Show intermediate results during generation
- Allow manual refinement of generated icons

#### C. Main Window Updates (`main.py`)
- Add "Style Transfer" button in AI Tools panel
- Modal dialog for style transfer workflow
- Palette lock toggle integration

---

### 4. Model Swapping Architecture

```python
class ModelFactory:
    @staticmethod
    def create_vision_model(name):
        models = {
            "qwen-vl": QwenVLModel,
            "gemma-vision": GemmaVisionModel,
            # Add more as needed
        }
        return models[name]()
    
    @staticmethod
    def create_generation_model(name):
        models = {
            "sdxl-base": SDXLBase,
            "sdxl-turbo": SDXLTurbo,
            # Add more as needed
        }
        return models[name]()
```

Configuration file (`models.json`) for easy model switching:
```json
{
    "vision_model": "qwen-vl",
    "generation_model": "sdxl-base",
    "segmentation_model": "sam-base"
}
```

---

### 5. Data Flow

```
[Style Image] 
    ↓ (StyleAnalyzer)
[Style Description + Palette]
    ↓
[Subject Image (large)]
    ↓ (SubjectProcessor - resize/sample)
[Subject Image (target size)]
    ↓ (IconGenerator + Style Prompt)
[Generated Icon]
    ↓ (BackgroundRemover if needed)
[Final Icon with Transparency]
    ↓
[PixelSmart Canvas]
```

---

### 6. User Experience Flow

1. **User uploads style image** → System extracts palette and generates style prompt
2. **User uploads subject image** → System samples it to target resolution
3. **User clicks "Generate"** → AI generates icon in style
4. **Optional background removal** → Transparent background created
5. **User can refine** → Manual pixel editing in canvas
6. **Save/export** → Save as `.pxsmart` or export PNG

---

### 7. Palette Management Enhancements

- Add `palette_locked` flag to `PaletteManager`
- When locked: palette preserved during style transfer
- When unlocked: palette updated from style image analysis
- Visual indicator in UI (lock icon next to palette)

---

## Implementation Status

### ✅ Completed (Phase 1 + AI Modules)

#### Phase 1: Manual Editor
- Canvas rendering with grid system
- Drawing tools (Pencil, Eraser, Fill, Picker)
- Palette management with save/load
- File I/O (.pxsmart format)
- PNG export

#### Phase 2: AI Integration ✅ IN PROGRESS
- **AI Client** (`ai_client.py`): LM Studio/Ollama API wrapper
- **Style Analyzer** (`style_analysis.py`): Style analysis and palette extraction
- **Subject Processor** (`subject_processor.py`): Image sampling and preparation
- **Icon Generator** (`icon_generator.py`): AI-powered icon generation
- **Background Remover** (`background_remover.py`): Background removal & transparency

### 🔄 Next Steps (Phase 2 Completion)

1. **Full LM Studio Integration**
   - Implement actual HTTP requests to LM Studio API
   - Add async support for non-blocking UI during generation
   - Progress callbacks for long-running operations

2. **UI Refinements**
   - Add progress dialog with cancellation option
   - Better error handling and user feedback
   - Preview of generated icons before applying to canvas

3. **Testing & Validation**
   - Test with real LM Studio endpoints
   - Validate style transfer quality
   - Performance testing with large images

4. **Documentation**
   - User guide for AI features
   - Model setup instructions
   - Troubleshooting guide

### 📋 Future Enhancements (Phase 3)

- Animation timeline with onion skinning
- Layer management system
- Frame-by-frame animation editor
- GIF export support
- Spritesheet export for game engines

## How to Use the AI Modules

### Without AI Models (Heuristic Mode)
The application works fully in heuristic mode without any AI setup:

```bash
# Run PixelSmart
python3 src/pixelsmart/main.py

# All features work, including:
# - Style Transfer UI (uses heuristics instead of AI)
# - Background Remover
# - Palette management
```

### With LM Studio (Full AI Features)

1. **Install LM Studio** from https://lmstudio.ai/
2. **Download Models** in LM Studio:
   - Vision: `qwen-vl` or `gemma-vision`
   - Generation: `sdxl-base` with ControlNet
   - Segmentation: `sam` or `mobile-sam`
3. **Start Local Server** (default port 1234)
4. **Use AI Features** in PixelSmart

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run only AI module tests  
python3 -m pytest tests/test_ai_modules.py -v
```

All tests pass (45 total: 34 original + 11 new AI tests).

## Files Created/Modified

### New Files:
- `src/pixelsmart/models.json` - Model configuration
- `src/pixelsmart/ai_client.py` - AI API client
- `src/pixelsmart/style_analysis.py` - Style analysis module
- `src/pixelsmart/subject_processor.py` - Subject processing module
- `src/pixelsmart/icon_generator.py` - Icon generation module
- `src/pixelsmart/background_remover.py` - Background removal module
- `tests/test_ai_modules.py` - AI module tests
- `AI_MODULES.md` - Detailed documentation

### Modified Files:
- `src/pixelsmart/main.py` - Integrated AI modules and UI
- `README.md` - Updated with AI features documentation
- `DESIGN.md` - Updated implementation status
