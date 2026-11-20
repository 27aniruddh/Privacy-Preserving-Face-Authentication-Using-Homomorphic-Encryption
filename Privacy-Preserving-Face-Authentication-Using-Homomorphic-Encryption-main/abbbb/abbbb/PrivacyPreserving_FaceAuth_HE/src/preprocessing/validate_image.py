"""Image validation for face detection"""
from pathlib import Path
import os
from PIL import Image

class ImageValidator:
    """Validates images contain faces"""
    
    def __init__(self):
        self.valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        self.min_image_size = 100  # minimum width/height in pixels
    
    def validate(self, image_path):
        """Validate image file"""
        try:
            path = Path(image_path)
            
            # Check extension
            if path.suffix.lower() not in self.valid_extensions:
                return False, "Invalid file format"
            
            # Check if file exists and has size
            if not path.exists():
                return False, "Image file not found"
            
            file_size = path.stat().st_size
            if file_size == 0:
                return False, "Image file is empty"
            
            if file_size > 16 * 1024 * 1024:  # 16MB max
                return False, "Image file too large"
            
            # Verify it's actually a valid image
            try:
                img = Image.open(str(image_path))
                img.verify()
                width, height = img.size
                
                if width < self.min_image_size or height < self.min_image_size:
                    return False, f"Image too small ({width}x{height}). Minimum {self.min_image_size}x{self.min_image_size}"
                
                print(f"[DEBUG] Image validated: {width}x{height}, format={img.format}, size={file_size} bytes")
                return True, "Valid image"
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"
        
        except Exception as e:
            return False, f"Error validating image: {str(e)}"

    def validate_uploaded_image(self, image_path):
        """Validate uploaded image (compat for app usage)"""
        return self.validate(image_path)
