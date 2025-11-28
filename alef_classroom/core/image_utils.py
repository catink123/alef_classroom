from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

def compress_image(image_file, max_width=1200, max_height=1200, quality=85):
    """
    Compress an image file to reduce file size.
    
    Args:
        image_file: Django ImageField file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed image file
    """
    if not image_file:
        return image_file
    
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Resize if necessary
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save compressed image
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Get the original filename
        filename = image_file.name
        if not filename.lower().endswith('.jpg'):
            filename = os.path.splitext(filename)[0] + '.jpg'
        
        # Return compressed image as ContentFile
        return ContentFile(output.getvalue(), name=filename)
    
    except Exception as e:
        # If compression fails, return original
        print(f"Image compression failed: {e}")
        return image_file
