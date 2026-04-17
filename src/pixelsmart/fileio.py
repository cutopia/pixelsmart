"""File I/O module for PixelSmart project files"""
import os
import zipfile
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage


class ProjectIO:
    """Handles saving and loading .pxsmart project files"""
    
    PROJECT_VERSION = "1.0"
    
    def __init__(self):
        self.last_loaded_path = None
    
    def save_project(self, canvas, filepath, palette_manager=None):
        """
        Save a PixelSmart project to a .pxsmart file
        
        Args:
            canvas: The PixelSmartCanvas instance
            filepath: Path to save the project (.pxsmart extension)
            palette_manager: Optional PaletteManager instance
        """
        # Ensure .pxsmart extension
        if not filepath.endswith('.pxsmart'):
            filepath += '.pxsmart'
        
        try:
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Save manifest.json
                manifest = {
                    "version": self.PROJECT_VERSION,
                    "canvas_width": canvas.canvas_width,
                    "canvas_height": canvas.canvas_height,
                    "current_color": canvas.get_current_color(),
                    "zoom_level": canvas.zoom_level,
                    "offset_x": canvas.offset.x(),
                    "offset_y": canvas.offset.y()
                }
                
                # Save image as PNG
                temp_image_path = "/tmp/pixelsmart_temp.png"
                canvas.image.save(temp_image_path, "PNG")
                
                zf.write(temp_image_path, "canvas.png")
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))
                
                # Save palette if provided
                if palette_manager is not None:
                    temp_palette_path = "/tmp/pixelsmart_palette.json"
                    palette_manager.save_to_file(temp_palette_path)
                    zf.write(temp_palette_path, "palette.json")
                    os.remove(temp_palette_path)
                
                # Clean up temp image
                os.remove(temp_image_path)
            
            self.last_loaded_path = filepath
            return True
            
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def load_project(self, filepath):
        """
        Load a PixelSmart project from a .pxsmart file
        
        Args:
            filepath: Path to the .pxsmart file
            
        Returns:
            dict with canvas_image, palette_manager (optional), and metadata
        """
        if not filepath.endswith('.pxsmart'):
            filepath += '.pxsmart'
        
        try:
            result = {
                "success": False,
                "canvas_width": 32,
                "canvas_height": 32,
                "current_color": "#000000",
                "zoom_level": 20.0,
                "offset_x": 0,
                "offset_y": 0,
                "palette_manager": None
            }
            
            with zipfile.ZipFile(filepath, 'r') as zf:
                # Load manifest.json
                if "manifest.json" in zf.namelist():
                    manifest_data = zf.read("manifest.json")
                    manifest = json.loads(manifest_data)
                    
                    result["canvas_width"] = manifest.get("canvas_width", 32)
                    result["canvas_height"] = manifest.get("canvas_height", 32)
                    result["current_color"] = manifest.get("current_color", "#000000")
                    result["zoom_level"] = manifest.get("zoom_level", 20.0)
                    result["offset_x"] = manifest.get("offset_x", 0)
                    result["offset_y"] = manifest.get("offset_y", 0)
                
                # Load canvas.png
                if "canvas.png" in zf.namelist():
                    temp_dir = "/tmp/pixelsmart_extract"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_image_path = os.path.join(temp_dir, "canvas.png")
                    zf.extract("canvas.png", temp_dir)
                    
                    result["canvas_image"] = QImage(temp_image_path)
                    # Don't delete immediately - it's used later
                else:
                    # Create empty image if not found
                    width = result["canvas_width"]
                    height = result["canvas_height"]
                    result["canvas_image"] = QImage(width, height, QImage.Format_ARGB32)
                    result["canvas_image"].fill(Qt.transparent)
                
                # Load palette if present
                if "palette.json" in zf.namelist():
                    temp_palette_path = os.path.join(temp_dir, "palette.json")
                    zf.extract("palette.json", temp_dir)
                    
                    from pixelsmart.palette import PaletteManager
                    result["palette_manager"] = PaletteManager()
                    result["palette_manager"].load_from_file(temp_palette_path)
                    os.remove(temp_palette_path)
            
            # Clean up temp directory
            if 'temp_dir' in locals():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            self.last_loaded_path = filepath
            result["success"] = True
            return result
            
        except Exception as e:
            print(f"Error loading project: {e}")
            # Clean up temp directory on error
            if 'temp_dir' in locals():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            return {"success": False, "error": str(e)}
