"""
Generate an icon for the VSCode Extension Resetter.
"""

import base64
import os
from PIL import Image, ImageDraw, ImageFont

def generate_icon():
    """
    Generate a simple icon for the application.
    """
    # Create a new image with a white background
    img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue square with rounded corners
    draw.rounded_rectangle([(20, 20), (236, 236)], radius=30, fill=(0, 122, 204, 255))
    
    # Draw a white "R" in the center
    try:
        font = ImageFont.truetype("arial.ttf", 150)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((85, 50), "R", fill=(255, 255, 255, 255), font=font)
    
    # Save the image as PNG
    img.save("icon.png")
    
    # Save as ICO for Windows
    img.save("icon.ico", format="ICO", sizes=[(32, 32), (64, 64), (128, 128), (256, 256)])
    
    print("Icon files generated: icon.png and icon.ico")

if __name__ == "__main__":
    generate_icon()
