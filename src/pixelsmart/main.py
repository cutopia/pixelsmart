import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QFrame, QLabel, QFileDialog, QMessageBox,
                               QColorDialog, QGridLayout, QProgressDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, Qt as QtGuiQt
from pixelsmart.canvas import PixelSmartCanvas
from pixelsmart.palette import PaletteManager
from pixelsmart.fileio import ProjectIO
from pixelsmart.vision import VisionModel
from pixelsmart.vision_worker import VisionWorker


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
        
        # Initialize vision model (will be loaded lazily)
        self.vision_model = VisionModel()
        
        # Initialize vision worker for async operations
        self.vision_worker = VisionWorker(self)

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
        
        # Connect vision worker signals
        self.vision_worker.started.connect(self._on_vision_operation_started)
        self.vision_worker.progress.connect(self._on_vision_progress)
        self.vision_worker.finished.connect(self._on_vision_operation_finished)
        self.vision_worker.error.connect(self._on_vision_operation_error)

        # Right Sidebar: AI & Palette
        right_sidebar = QFrame()
        right_sidebar.setFixedWidth(250)
        right_sidebar.setStyleSheet("background-color: #3c3c3c; border-left: 1px solid #1a1a1a;")
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setAlignment(Qt.AlignTop)

        ai_label = QLabel("AI Tools")
        ai_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(ai_label)
        
        # AI Pixelizer button
        self.ai_pixelizer_btn = QPushButton("AI Pixelizer")
        self.ai_pixelizer_btn.clicked.connect(self.run_ai_pixelizer)
        right_layout.addWidget(self.ai_pixelizer_btn)
        
        # Background Remover button
        self.bg_remover_btn = QPushButton("Background Remover")
        self.bg_remover_btn.clicked.connect(self.run_background_remover)
        right_layout.addWidget(self.bg_remover_btn)
        
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
    
    def _on_vision_operation_started(self):
        """Called when vision operation starts - show progress dialog"""
        # Create a modal progress dialog that can be cancelled
        self._vision_progress_dialog = QProgressDialog(
            "Processing image... Please wait...", 
            "Cancel", 
            0, 
            100, 
            self,
            Qt.WindowTitleHint | Qt.CustomizeWindowHint
        )
        self._vision_progress_dialog.setWindowModality(Qt.WindowModal)
        self._vision_progress_dialog.setWindowTitle("AI Processing")
        self._vision_progress_dialog.setAutoClose(False)
        self._vision_progress_dialog.setValue(0)
        self._vision_progress_dialog.show()
    
    def _on_vision_progress(self, message):
        """Called with progress updates from the vision worker"""
        if hasattr(self, '_vision_progress_dialog') and self._vision_progress_dialog:
            self._vision_progress_dialog.setLabelText(message)
            # Increment progress bar
            current = self._vision_progress_dialog.value()
            self._vision_progress_dialog.setValue(min(current + 10, 90))
    
    def _on_vision_operation_finished(self, result):
        """Called when vision operation completes successfully"""
        if hasattr(self, '_vision_progress_dialog') and self._vision_progress_dialog:
            self._vision_progress_dialog.close()
            self._vision_progress_dialog = None
        
        # Show the result
        result_dialog = QMessageBox(self)
        result_dialog.setWindowTitle("AI Processing Results")
        display_text = result[:500] + "..." if len(result) > 500 else result
        result_dialog.setText(display_text)
        result_dialog.exec()
    
    def _on_vision_operation_error(self, error_message):
        """Called when vision operation encounters an error"""
        if hasattr(self, '_vision_progress_dialog') and self._vision_progress_dialog:
            self._vision_progress_dialog.close()
            self._vision_progress_dialog = None
        
        QMessageBox.critical(self, "AI Processing Error", error_message)
    
    def run_ai_pixelizer(self):
        """Run AI Pixelizer to convert current canvas or imported image to pixel art"""
        # Check if vision model is loaded
        if not self.vision_model.is_loaded():
            QMessageBox.information(self, "Loading Model", 
                                  "Loading vision model (first time use may take a moment)...")
            if not self.vision_model.load():
                QMessageBox.critical(self, "Error", 
                                   "Failed to load vision model. Check that transformers and torch are installed.")
                return
        
        # Get current canvas image or prompt for file
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image for Pixelization", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            from PIL import Image
            
            # Load image
            image = Image.open(filepath)
            
            # Set up the worker with the vision model and run the operation
            self.vision_worker.set_vision_model(self.vision_model)
            self.vision_worker.run_pixelizer(image)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")
    
    def run_background_remover(self):
        """Run background removal on current canvas or imported image"""
        # Check if vision model is loaded
        if not self.vision_model.is_loaded():
            QMessageBox.information(self, "Loading Model", 
                                  "Loading vision model (first time use may take a moment)...")
            if not self.vision_model.load():
                QMessageBox.critical(self, "Error", 
                                   "Failed to load vision model. Check that transformers and torch are installed.")
                return
        
        # Get current canvas image or prompt for file
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image for Background Removal", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            from PIL import Image
            
            # Load image
            image = Image.open(filepath)
            
            # Set up the worker with the vision model and run the operation
            self.vision_worker.set_vision_model(self.vision_model)
            self.vision_worker.run_background_remover(
                image,
                "Identify the main subject/object in this image and describe what should be kept vs removed as background."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
