"""Worker thread for vision model operations."""

from PySide6.QtCore import QThread, Signal


class VisionWorker(QThread):
    """Worker thread for running vision model operations without blocking the UI."""
    
    # Signals for progress updates and results
    started = Signal()
    progress = Signal(str)  # Progress message
    finished = Signal(str)  # Result text when complete
    error = Signal(str)     # Error message if something goes wrong
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._operation = None
        self._image = None
        self._prompt = None
        self._vision_model = None
    
    def set_vision_model(self, vision_model):
        """Set the vision model to use for operations."""
        self._vision_model = vision_model
    
    def run_pixelizer(self, image):
        """Schedule a pixelization operation."""
        self._operation = 'pixelizer'
        self._image = image
        self.start()
    
    def run_background_remover(self, image, prompt):
        """Schedule a background removal analysis operation."""
        self._operation = 'background_remover'
        self._image = image
        self._prompt = prompt
        self.start()
    
    def run(self):
        """Execute the scheduled operation in the worker thread."""
        try:
            self.started.emit()
            
            if not self._vision_model or not self._vision_model.is_loaded():
                self.error.emit("Vision model not loaded. Please load the model first.")
                return
            
            # Simulate progress updates
            self.progress.emit("Analyzing image...")
            
            if self._operation == 'pixelizer':
                result = self._vision_model.convert_to_pixel_art(self._image)
                self.finished.emit(result)
            elif self._operation == 'background_remover':
                self.progress.emit("Identifying main subject...")
                analysis = self._vision_model.analyze_image(
                    self._image, 
                    self._prompt or "Describe the main subject in this image."
                )
                self.finished.emit(analysis)
            else:
                self.error.emit(f"Unknown operation: {self._operation}")
                
        except Exception as e:
            self.error.emit(str(e))
