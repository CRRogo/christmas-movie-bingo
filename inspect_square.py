"""
Quick script to inspect an extracted square and see what it contains.
"""

from PIL import Image, ImageDraw

# Load a square from the first column
square_path = "squares_final/square_0_0.png"
square = Image.open(square_path)

print(f"Square size: {square.size}")
print(f"Square mode: {square.mode}")

# Create a visualization showing the square with a border
vis = square.copy()
draw = ImageDraw.Draw(vis)
draw.rectangle([0, 0, square.size[0]-1, square.size[1]-1], outline='blue', width=2)

vis.save("square_inspection.png")
print(f"Saved inspection image: square_inspection.png")

