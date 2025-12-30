"""
Create a background template using the correct grid bounds from smart extraction.
"""

from PIL import Image, ImageDraw
import json

# Load the original image
img = Image.open("unnamed.webp")
width, height = img.size

# Load metadata to get the grid bounds
with open("squares/metadata.json", 'r') as f:
    metadata = json.load(f)

grid_bounds = metadata['grid_bounds']
grid_lines = metadata['grid_lines']

print(f"Image size: {width}x{height}")
print(f"Grid bounds: {grid_bounds}")
print(f"Grid lines: {grid_lines}")

# Create background template with transparent grid area
background = img.copy()

# Convert to RGBA if needed
if background.mode != 'RGBA':
    background = background.convert('RGBA')

# Create a mask for the grid area (make it transparent)
mask = Image.new('L', background.size, 255)  # White = opaque
draw = ImageDraw.Draw(mask)

# Make the entire grid area transparent
# Use the grid bounds
grid_left = grid_bounds['left']
grid_top = grid_bounds['top']
grid_right = grid_bounds['right']
grid_bottom = grid_bounds['bottom']

draw.rectangle([grid_left, grid_top, grid_right, grid_bottom], fill=0)  # Black = transparent

# Apply mask
background.putalpha(mask)

# Save background template
background.save("background_template.png", "PNG")
print(f"Saved background template: background_template.png")

# Also copy to public folder
import shutil
shutil.copy("background_template.png", "public/background_template.png")
print(f"Copied to public/background_template.png")

