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

## Next Steps

Would you like me to:
1. **Proceed with updating DESIGN.md** with this specification?
2. **Refine any specific aspect** of the design first?
3. **Start implementation** after design approval?

Please confirm if this design aligns with your vision, and I'll update the DESIGN.md file.
