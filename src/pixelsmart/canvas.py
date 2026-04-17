import sys
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QWheelEvent, QMouseEvent

class PixelSmartCanvas(QWidget):
    def __init__(self, width=32, height=32):
        super().__init__()
        self.canvas_width = width
        self.canvas_height = height
        
        # Image buffer (The actual pixel data)
        self.image = QImage(self.canvas_width, self.canvas_height, QImage.Format_ARGB32)
        self.image.fill(Qt.transparent)
        
        # View state
        self.zoom_level = 20.0  # pixels on screen per canvas pixel
        self.offset = QPointF(0, 0)
        self.last_mouse_pos = QPointF(0, 0)
        self.is_panning = False

        # Tool state
        self.active_tool = "pencil"
        self.current_color = QColor("#000000")
        self.is_drawing = False
        
        # Color picker callback for main window updates
        self.color_picked = None

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Draw background
        painter.fillRect(self.rect(), QColor("#2c2c2c"))

        # Calculate drawing area
        x = int(self.offset.x())
        y = int(self.offset.y())
        w = int(self.canvas_width * self.zoom_level)
        h = int(self.canvas_height * self.zoom_level)

        # Draw the pixel image (Nearest Neighbor scaling by PySide6 when using drawImage with target rect)
        target_rect = QRectF(x, y, w, h)
        painter.drawImage(target_rect.toRect(), self.image)

        # Draw grid
        if self.zoom_level > 5:
            pen = QPen(QColor("#444444"))
            pen.setWidth(1)
            painter.setPen(pen)
            
            for i in range(self.canvas_width + 1):
                px = x + i * self.zoom_level
                painter.drawLine(int(px), y, int(px), y + h)
            
            for j in range(self.canvas_height + 1):
                py = y + j * self.zoom_level
                painter.drawLine(x, int(py), x + w, int(py))

    def wheelEvent(self, event: QWheelEvent):
        # Zooming centered on mouse cursor
        mouse_pos = event.position()
        
        old_zoom = self.zoom_level
        if event.angleDelta().y() > 0:
            self.zoom_level *= 1.2
        else:
            self.zoom_level /= 1.2
        
        self.zoom_level = max(1.0, min(self.zoom_level, 100.0))
        
        # Adjust offset to zoom toward mouse cursor
        zoom_factor = self.zoom_level / old_zoom
        self.offset.setX(mouse_pos.x() - (mouse_pos.x() - self.offset.x()) * zoom_factor)
        self.offset.setY(mouse_pos.y() - (mouse_pos.y() - self.offset.y()) * zoom_factor)
        
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.draw_at_mouse(event.position())
            self.setCursor(Qt.CrossCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning:
            current_pos = event.position()
            delta = current_pos - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = current_pos
            self.update()
        elif self.is_drawing:
            self.draw_at_mouse(event.position())

    def draw_at_mouse(self, pos):
        # Convert screen coordinates to canvas pixel coordinates
        pixel_x = int((pos.x() - self.offset.x()) / self.zoom_level)
        pixel_y = int((pos.y() - self.offset.y()) / self.zoom_level)

        # Boundary check
        if 0 <= pixel_x < self.canvas_width and 0 <= pixel_y < self.canvas_height:
            if self.active_tool == "pencil":
                self.image.setPixelColor(pixel_x, pixel_y, self.current_color)
            elif self.active_tool == "eraser":
                # Eraser sets to transparent (or background color)
                self.image.setPixelColor(pixel_x, pixel_y, Qt.transparent)
            elif self.active_tool == "fill":
                self.flood_fill(pixel_x, pixel_y, self.current_color)
            elif self.active_tool == "picker":
                sampled_color = self.image.pixelColor(pixel_x, pixel_y)
                if sampled_color.isValid():
                    self.set_current_color(sampled_color)
            
            self.update()

    def set_current_color(self, color):
        """Set the current drawing color (accepts string or QColor)"""
        from PySide6.QtGui import QColor
        if isinstance(color, str):
            self.current_color = QColor(color)
        else:
            self.current_color = color
    
    def get_current_color(self):
        """Get the current drawing color"""
        return self.current_color.name() if hasattr(self.current_color, 'name') else self.current_color

    def flood_fill(self, start_x, start_y, new_color):
        """Flood fill algorithm using a stack-based approach"""
        # Get the color at the starting position
        old_color = self.image.pixelColor(start_x, start_y)
        
        # If the new color is the same as old color, do nothing
        if old_color == new_color:
            return
        
        # Use a stack for iterative flood fill
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            # Check bounds
            if not (0 <= x < self.canvas_width and 0 <= y < self.canvas_height):
                continue
            
            # Get current color at this position
            current_color = self.image.pixelColor(x, y)
            
            # If current color matches old color, fill it
            if current_color == old_color:
                self.image.setPixelColor(x, y, new_color)
                
                # Add neighboring pixels to stack (4-directional)
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))