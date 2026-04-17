import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QFrame, QLabel, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from pixelsmart.canvas import PixelSmartCanvas
from pixelsmart.palette import PaletteManager
from pixelsmart.fileio import ProjectIO


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelSmart")
        self.resize(1200, 800)
        
        # Initialize managers
        self.palette_manager = PaletteManager()
        self.file_io = ProjectIO()

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

        ai_label = QLabel("AI Tools")
        ai_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(ai_label)
        
        right_layout.addWidget(QPushButton("AI Pixelizer"))
        right_layout.addWidget(QPushButton("Background Remover"))
        
        right_layout.addSpacing(20)
        
        palette_label = QLabel("Palette")
        palette_label.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(palette_label)
        
        # Placeholder for palette display
        palette_frame = QFrame()
        palette_frame.setMinimumHeight(150)
        palette_frame.setStyleSheet("background-color: #2c2c2c; border: 1px solid #444;")
        right_layout.addWidget(palette_frame)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
