import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QFrame, QLabel, QFileDialog, QMessageBox,
                               QColorDialog, QGridLayout, QLineEdit, QSlider, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, Qt as QtGuiQt
from pixelsmart.canvas import PixelSmartCanvas
from pixelsmart.palette import PaletteManager
from pixelsmart.fileio import ProjectIO

# Import AI modules
try:
    from pixelsmart.style_analysis import StyleAnalyzer
    from pixelsmart.subject_processor import SubjectProcessor
    from pixelsmart.icon_generator import IconGenerator
    from pixelsmart.background_remover import BackgroundRemover
    HAS_AI_MODULES = True
except ImportError as e:
    # AI modules not available, disable AI features
    print(f"Warning: Could not import AI modules: {e}")
    HAS_AI_MODULES = False


class SwatchButton(QPushButton):
    """Custom QPushButton that handles single and double-click events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_count = 0
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_count += 1
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_count == 1:
            # Single click - emit clicked signal
            self.clicked.emit()
        self.click_count = 0
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Reset click count on double click
            self.click_count = 0
            self.handleDoubleClicked()
        super().mouseDoubleClickEvent(event)
    
    def handleDoubleClicked(self):
        """Handle double-click - can be overridden or connected to slots"""
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelSmart")
        self.resize(1200, 800)
        
        # Initialize managers
        self.palette_manager = PaletteManager()
        self.file_io = ProjectIO()
        
        # Initialize AI components (if available)
        if HAS_AI_MODULES:
            self.style_analyzer = StyleAnalyzer()
            self.subject_processor = SubjectProcessor()
            self.icon_generator = IconGenerator()
            self.background_remover = BackgroundRemover()
            
            # Style transfer state
            self.style_image_path = None
            self.subject_image_path = None
            self.generated_icon = None
            self.palette_locked = False
        else:
            self.style_analyzer = None
            self.subject_processor = None
            self.icon_generator = None
            self.background_remover = None
            self.style_image_path = None
            self.subject_image_path = None
            self.generated_icon = None
            self.palette_locked = False

        # Central Widget and Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(self.new_project)
        
        open_action = file_menu.addAction("Open Project...")
        open_action.triggered.connect(self.open_project)
        
        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(self.save_project)
        
        save_as_action = file_menu.addAction("Save Project As...")
        save_as_action.triggered.connect(lambda: self.save_project(save_as=True))
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction("Export as PNG...")
        export_action.triggered.connect(self.export_png)

        # Left Sidebar: Tools
        left_sidebar = QFrame()
        left_sidebar.setFixedWidth(60)
        left_sidebar.setStyleSheet("background-color: #3c3c3c; border-right: 1px solid #1a1a1a;")
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(5, 10, 5, 10)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignTop)

        tools = ["Pencil", "Eraser", "Fill", "Picker"]
        self.tool_buttons = {}
        for tool in tools:
            btn = QPushButton(tool)
            btn.setToolTip(tool)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tool: self.select_tool(t))
            self.tool_buttons[tool] = btn
            left_layout.addWidget(btn)
        
        # Set default selection (Pencil)
        self.tool_buttons["Pencil"].setChecked(True)

        # Initialize canvas (must be before menu action handlers that use it)
        self.canvas = PixelSmartCanvas()

        # Right Sidebar: AI & Palette
        right_sidebar = QFrame()
        right_sidebar.setFixedWidth(250)
        right_sidebar.setStyleSheet("background-color: #3c3c3c; border-left: 1px solid #1a1a1a;")
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setAlignment(Qt.AlignTop)

        # AI Tools Section
        ai_section = QFrame()
        ai_section.setStyleSheet("background-color: #2c2c2c; border-radius: 5px;")
        ai_layout = QVBoxLayout(ai_section)
        ai_layout.setContentsMargins(10, 10, 10, 10)
        
        ai_label = QLabel("AI Tools")
        ai_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        ai_layout.addWidget(ai_label)
        
        # Style Transfer Section
        style_transfer_section = QFrame()
        style_transfer_section.setStyleSheet("background-color: #222; border-radius: 3px;")
        style_transfer_layout = QVBoxLayout(style_transfer_section)
        style_transfer_layout.setContentsMargins(5, 5, 5, 5)
        
        style_label = QLabel("Style Transfer")
        style_label.setStyleSheet("color: #aaa; font-size: 10px; margin-bottom: 5px;")
        style_transfer_layout.addWidget(style_label)
        
        # Style image upload
        self.style_upload_btn = QPushButton("Upload Style Image...")
        self.style_upload_btn.setFixedHeight(25)
        self.style_upload_btn.clicked.connect(self.upload_style_image)
        style_transfer_layout.addWidget(self.style_upload_btn)
        
        self.style_preview_label = QLabel("No style image")
        self.style_preview_label.setStyleSheet("color: #666; font-size: 9px;")
        self.style_preview_label.setFixedHeight(20)
        style_transfer_layout.addWidget(self.style_preview_label)
        
        # Subject image upload
        self.subject_upload_btn = QPushButton("Upload Subject Image...")
        self.subject_upload_btn.setFixedHeight(25)
        self.subject_upload_btn.clicked.connect(self.upload_subject_image)
        style_transfer_layout.addWidget(self.subject_upload_btn)
        
        self.subject_preview_label = QLabel("No subject image")
        self.subject_preview_label.setStyleSheet("color: #666; font-size: 9px;")
        self.subject_preview_label.setFixedHeight(20)
        style_transfer_layout.addWidget(self.subject_preview_label)
        
        # Output resolution selector
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Output:"))
        self.resolution_combo = QFrame()
        self.resolution_combo.setStyleSheet("background-color: white; border-radius: 3px;")
        resolution_layout.addWidget(self.resolution_combo)
        style_transfer_layout.addLayout(resolution_layout)
        
        # Style strength slider
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(QLabel("Style Strength:"))
        self.style_strength_slider = QSlider(Qt.Horizontal)
        self.style_strength_slider.setRange(0, 100)
        self.style_strength_slider.setValue(70)
        self.style_strength_slider.setFixedWidth(120)
        strength_layout.addWidget(self.style_strength_slider)
        style_transfer_layout.addLayout(strength_layout)
        
        # Palette lock checkbox
        self.palette_lock_checkbox = QCheckBox("Lock Current Palette")
        self.palette_lock_checkbox.setChecked(False)
        self.palette_lock_checkbox.stateChanged.connect(self.toggle_palette_lock)
        style_transfer_layout.addWidget(self.palette_lock_checkbox)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Icon")
        self.generate_btn.setFixedHeight(30)
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 3px;")
        self.generate_btn.clicked.connect(self.generate_icon)
        style_transfer_layout.addWidget(self.generate_btn)
        
        ai_layout.addWidget(style_transfer_section)
        
        # Background Remover button
        bg_remove_btn = QPushButton("Background Remover")
        bg_remove_btn.setFixedHeight(25)
        bg_remove_btn.clicked.connect(self.remove_background)
        right_layout.addWidget(bg_remove_btn)
        
        right_layout.addSpacing(20)
        
        palette_label = QLabel("Palette")
        palette_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(palette_label)
        
        # Palette display frame with color swatches (24 slots in 6 columns x 4 rows grid)
        self.palette_frame = QFrame()
        self.palette_frame.setMinimumHeight(180)
        self.palette_frame.setStyleSheet("background-color: #2c2c2c; border: 1px solid #444;")
        self.palette_layout = QGridLayout(self.palette_frame)
        self.palette_layout.setContentsMargins(5, 5, 5, 5)
        self.palette_layout.setAlignment(QtGuiQt.AlignTop)
        self.palette_layout.setSpacing(5)
        
        # Create color swatches grid (6 columns x 4 rows = 24 slots)
        self.color_swatches = []
        for i in range(24):  # Show up to 24 colors
            swatch = SwatchButton()
            swatch.setFixedSize(30, 30)
            swatch.index = i  # Store index for double-click event
            swatch.setStyleSheet("border: 1px dashed #555; background-color: #3c3c3c;")
            swatch.setToolTip(f"Palette slot {i}\nDouble-click to pick color")
            
            # Override handleDoubleClicked for this specific button
            def make_handler(idx):
                return lambda: self.pick_palette_color(idx)
            
            # Single click handler for selecting color
            swatch.clicked.connect(lambda checked=False, idx=i: self.select_palette_color(idx))
            
            # Double click handler for picking new color
            swatch.handleDoubleClicked = make_handler(i)
            
            row = i // 6
            col = i % 6
            self.palette_layout.addWidget(swatch, row, col)
            self.color_swatches.append(swatch)
        
        right_layout.addWidget(self.palette_frame)
        
        # Palette management buttons
        palette_btn_layout = QHBoxLayout()
        
        add_color_btn = QPushButton("+")
        add_color_btn.setFixedSize(25, 25)
        add_color_btn.setToolTip("Add current canvas color to palette")
        add_color_btn.clicked.connect(self.add_current_color_to_palette)
        palette_btn_layout.addWidget(add_color_btn)
        
        remove_color_btn = QPushButton("-")
        remove_color_btn.setFixedSize(25, 25)
        remove_color_btn.setToolTip("Remove selected color from palette")
        remove_color_btn.clicked.connect(self.remove_selected_color_from_palette)
        palette_btn_layout.addWidget(remove_color_btn)
        
        clear_palette_btn = QPushButton("Clear")
        clear_palette_btn.setFixedWidth(60)
        clear_palette_btn.setToolTip("Reset to default colors")
        clear_palette_btn.clicked.connect(self.reset_palette)
        palette_btn_layout.addWidget(clear_palette_btn)
        
        right_layout.addLayout(palette_btn_layout)

        # Center Area (Canvas + Bottom Bar)
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        center_layout.addWidget(self.canvas, 1)

        # Bottom Bar: Layers & Animation
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(150)
        bottom_bar.setStyleSheet("background-color: #3c3c3c; border-top: 1px solid #1a1a1a;")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        
        bottom_layout.addWidget(QLabel("Layers & Animation Timeline (Placeholder)"), alignment=Qt.AlignCenter)

        center_layout.addWidget(bottom_bar)

        # Add sidebars and center area to main layout
        main_layout.addWidget(left_sidebar)
        main_layout.addWidget(center_area, 1)
        main_layout.addWidget(right_sidebar)

    def new_project(self):
        """Create a new project"""
        reply = QMessageBox.question(self, "New Project",
                                    "Are you sure? Unsaved changes will be lost.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.canvas.image.fill(Qt.transparent)
            # Reset palette to defaults on new project
            from pixelsmart.palette import PaletteManager
            self.palette_manager = PaletteManager()
            self.update_palette_display()
            self.canvas.update()
    
    def open_project(self):
        """Open a project file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "PixelSmart Projects (*.pxsmart);;All Files (*)"
        )
        
        if filepath:
            result = self.file_io.load_project(filepath)
            
            if result["success"]:
                # Update canvas dimensions and image
                self.canvas.canvas_width = result["canvas_width"]
                self.canvas.canvas_height = result["canvas_height"]
                
                # Create new QImage with loaded data
                from PySide6.QtGui import QImage
                self.canvas.image = result["canvas_image"]
                
                # Update view state
                self.canvas.zoom_level = result.get("zoom_level", 20.0)
                self.canvas.offset.setX(result.get("offset_x", 0))
                self.canvas.offset.setY(result.get("offset_y", 0))
                
                # Set current color if available
                if "current_color" in result:
                    from PySide6.QtGui import QColor
                    self.canvas.set_current_color(QColor(result["current_color"]))
                
                # Update palette manager if provided
                if result.get("palette_manager"):
                    self.palette_manager = result["palette_manager"]
                
                # Sync canvas current color with palette
                self.canvas.set_current_color(self.palette_manager.get_current_color())
                
                self.update_palette_display()
                self.canvas.update()
            else:
                QMessageBox.critical(self, "Error", f"Failed to open project: {result.get('error', 'Unknown error')}")
    
    def save_project(self, save_as=False):
        """Save the current project"""
        filepath = None
        
        if not save_as and self.file_io.last_loaded_path:
            filepath = self.file_io.last_loaded_path
        else:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Project", "", "PixelSmart Projects (*.pxsmart);;All Files (*)"
            )
        
        if filepath:
            # Sync canvas color to palette before saving
            canvas_color = self.canvas.get_current_color()
            if hasattr(canvas_color, 'name'):
                self.palette_manager.set_current_color_obj(canvas_color)
            
            success = self.file_io.save_project(self.canvas, filepath, self.palette_manager)
            
            if success:
                QMessageBox.information(self, "Success", f"Project saved to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save project")

    def export_png(self):
        """Export canvas as PNG image"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export as PNG", "", "PNG Images (*.png);;All Files (*)"
        )
        
        if filepath:
            if not filepath.endswith('.png'):
                filepath += '.png'
            
            success = self.canvas.image.save(filepath, "PNG")
            
            if success:
                QMessageBox.information(self, "Success", f"Image exported to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export image")

    def select_palette_color(self, index):
        """Select a color from the palette (single click)"""
        current_colors = self.palette_manager.colors
        
        if index < len(current_colors):
            # Existing color - select it
            color = current_colors[index]
            self.canvas.set_current_color(color)
            self.palette_manager.set_current_index(index)
        
        self.update_palette_display()
    
    def pick_palette_color(self, index):
        """Open color picker dialog to select a new color for the specified palette slot"""
        current_colors = self.palette_manager.colors
        
        # Set initial color based on existing color at this index, or black if empty
        if index < len(current_colors):
            existing_color = current_colors[index]
            initial_color = QColor(existing_color.name() if hasattr(existing_color, 'name') else '#000000')
        else:
            initial_color = QColor('#000000')
        
        color_dialog = QColorDialog(initial_color, self)
        color_dialog.setWindowTitle(f"Select Color for Slot {index}")
        color_dialog.setOption(QColorDialog.ShowAlphaChannel, False)
        
        if color_dialog.exec():
            selected_color = color_dialog.currentColor()
            if selected_color.isValid():
                # Add or update the palette slot
                while len(current_colors) <= index:
                    current_colors.append(QColor('#000000'))  # Fill gaps with black
                
                current_colors[index] = selected_color
                self.palette_manager.set_current_index(index)
                
                self.update_palette_display()
    
    def add_current_color_to_palette(self):
        """Add current canvas color to palette at first empty slot or append"""
        color = self.canvas.get_current_color()
        if not hasattr(color, 'name'):
            color_str = str(color)
        else:
            color_str = color.name()
        
        # Find first empty slot (None or transparent placeholder)
        current_colors = self.palette_manager.colors
        empty_index = None
        for i in range(len(current_colors)):
            c = current_colors[i]
            if not hasattr(c, 'name') or c.name() == '#000000' and i > 0:
                # Check if it's actually empty/placeholder
                if i >= len(self.palette_manager.get_all_colors()):
                    empty_index = i
                    break
        
        if empty_index is not None:
            current_colors[empty_index] = QColor(color_str)
            self.palette_manager.set_current_index(empty_index)
        else:
            # Append to end (max 24 slots)
            if len(current_colors) < 24:
                self.palette_manager.add_color(color_str)
                self.palette_manager.set_current_index(len(current_colors))
        
        self.update_palette_display()
    
    def remove_selected_color_from_palette(self):
        """Remove currently selected color from palette"""
        current_index = self.palette_manager.current_index
        
        # Don't allow removing the transparent slot (index 0) or if only 16 colors exist
        if current_index == 0:
            return  # Can't remove transparent slot
            
        if len(self.palette_manager.colors) > 16:
            del self.palette_manager.colors[current_index]
            # Adjust current index if needed
            if self.palette_manager.current_index >= len(self.palette_manager.colors):
                self.palette_manager.current_index = len(self.palette_manager.colors) - 1
        
        self.update_palette_display()
    
    def reset_palette(self):
        """Reset palette to default colors"""
        # Create new PaletteManager with defaults
        from pixelsmart.palette import PaletteManager
        self.palette_manager = PaletteManager()
        self.update_palette_display()
    
    def update_palette_display(self):
        """Update the visual display of palette colors"""
        current_index = self.palette_manager.current_index
        
        for i, swatch in enumerate(self.color_swatches):
            if i < len(self.palette_manager.colors):
                color = self.palette_manager.get_color(i)
                # Convert Qt.GlobalColor enums to QColor to avoid .name() issues
                if isinstance(color, QtGuiQt.GlobalColor):
                    color = QColor(color)
                hex_color = color.name() if hasattr(color, 'name') else str(color)
                
                # Check if this is the currently selected color
                if i == current_index:
                    swatch.setStyleSheet(f"background-color: {hex_color}; border: 3px solid #00FF00;")
                else:
                    swatch.setStyleSheet(f"background-color: {hex_color}; border: 2px solid #555;")
                
                swatch.setToolTip(hex_color)
            else:
                # Empty slot - show as dashed placeholder
                swatch.setStyleSheet("background-color: #3c3c3c; border: 1px dashed #555;")
                swatch.setToolTip(f"Empty slot {i} (click to add color)")
        
        # If current color is not in palette, highlight it on the canvas
        canvas_color = self.canvas.get_current_color()
        if hasattr(canvas_color, 'name'):
            canvas_hex = canvas_color.name()
            for i, swatch in enumerate(self.color_swatches):
                if i < len(self.palette_manager.colors):
                    color = self.palette_manager.get_color(i)
                    # Convert Qt.GlobalColor enums to QColor to avoid .name() issues
                    if isinstance(color, QtGuiQt.GlobalColor):
                        color = QColor(color)
                    hex_color = color.name() if hasattr(color, 'name') else str(color)
                    if hex_color == canvas_hex and i != current_index:
                        # Canvas color matches a palette entry but it's not selected
                        swatch.setStyleSheet(f"background-color: {hex_color}; border: 2px solid #FFFF00;")
    
    def select_tool(self, tool_name):
        """Select a drawing tool"""
        # Update canvas active tool
        tool_map = {
            "Pencil": "pencil",
            "Eraser": "eraser", 
            "Fill": "fill",
            "Picker": "picker"
        }
        self.canvas.active_tool = tool_map.get(tool_name, "pencil")
        
        # Update button states
        for name, btn in self.tool_buttons.items():
            btn.setChecked(name == tool_name)
        
        # Set cursor based on tool
        if tool_name == "Fill":
            self.setCursor(Qt.ArrowCursor)
        elif tool_name == "Picker":
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def upload_style_image(self):
        """Upload a style image for analysis"""
        if not HAS_AI_MODULES:
            QMessageBox.information(self, "AI Not Available", 
                                  "Style Transfer requires AI modules that are not installed.")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Style Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if filepath:
            self.style_image_path = filepath
            self.style_preview_label.setText(f"Style: {os.path.basename(filepath)}")
            
            # Analyze style (mock for now)
            try:
                result = self.style_analyzer.analyze_style(filepath, use_ai=False)
                self.style_description = result.get("description", "Pixel art style")
                self.extracted_palette = result.get("palette", [])
                
                if not self.palette_locked and self.extracted_palette:
                    # Update palette with extracted colors
                    for i, color_hex in enumerate(self.extracted_palette[:16]):
                        if i < len(self.palette_manager.colors):
                            self.palette_manager.colors[i] = QColor(color_hex)
            
            except Exception as e:
                QMessageBox.warning(self, "Style Analysis Warning", 
                                  f"Could not analyze style: {str(e)}")

    def upload_subject_image(self):
        """Upload a subject image for icon generation"""
        if not HAS_AI_MODULES:
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Subject Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if filepath:
            self.subject_image_path = filepath
            self.subject_preview_label.setText(f"Subject: {os.path.basename(filepath)}")

    def toggle_palette_lock(self, state):
        """Toggle palette lock state"""
        self.palette_locked = (state == Qt.Checked)

    def generate_icon(self):
        """Generate a pixel art icon using style transfer"""
        if not HAS_AI_MODULES:
            QMessageBox.information(self, "AI Not Available", 
                                  "Style Transfer requires AI modules that are not installed.")
            return
        
        if not self.style_image_path or not self.subject_image_path:
            QMessageBox.warning(self, "Missing Images",
                              "Please upload both a style image and a subject image.")
            return
        
        # Get generation parameters
        target_size = (64, 64)  # Default size
        style_strength = self.style_strength_slider.value() / 100.0
        
        # Show progress dialog
        progress = QMessageBox(self)
        progress.setWindowTitle("Generating Icon")
        progress.setText("AI is generating your icon...")
        progress.setStandardButtons(QMessageBox.NoButton)
        progress.show()
        
        QApplication.processEvents()
        
        try:
            # Sample subject to target size
            sampled_subject = self.subject_processor.sample_subject(
                self.subject_image_path, target_size
            )
            
            # Generate icon using AI (mock implementation for now)
            prompt = f"{self.style_description}, pixel art version of this image"
            generated = self.icon_generator.generate_icon(
                prompt,
                None,  # Would use base_image_path in full implementation
                target_size,
                style_strength
            )
            
            # Apply palette constraint if not locked
            if not self.palette_locked and hasattr(self, 'extracted_palette'):
                generated = self.icon_generator.constrain_to_palette(
                    generated, self.extracted_palette[:16]
                )
            
            # Update canvas with result
            self.canvas.image = generated
            self.canvas.update()
            
            progress.close()
            QMessageBox.information(self, "Success", 
                                  f"Icon generated successfully!\nSize: {target_size[0]}x{target_size[1]}")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Generation Error",
                               f"Failed to generate icon: {str(e)}")

    def remove_background(self):
        """Remove background from current canvas or selected image"""
        if not HAS_AI_MODULES:
            return
        
        # For now, use heuristic background removal
        try:
            width = self.canvas.image.width()
            height = self.canvas.image.height()
            
            # Create a copy of the image
            result = QImage(width, height, QImage.Format_ARGB32)
            result.fill(Qt.transparent)
            
            # Heuristic: keep center region, remove edges
            margin_x = int(width * 0.1)
            margin_y = int(height * 0.1)
            
            for y in range(height):
                for x in range(width):
                    pixel = self.canvas.image.pixel(x, y)
                    
                    # Check if pixel is near edge
                    is_edge = (
                        x < margin_x or 
                        x >= width - margin_x or
                        y < margin_y or 
                        y >= height - margin_y
                    )
                    
                    if not is_edge:
                        result.setPixel(x, y, pixel)
            
            self.canvas.image = result
            self.canvas.update()
            QMessageBox.information(self, "Success", "Background removal applied (heuristic)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to remove background: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
