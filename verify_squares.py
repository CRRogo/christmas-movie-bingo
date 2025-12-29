"""
Create a visual verification by arranging extracted squares in a grid.
This helps verify that squares are extracted correctly.
"""

from PIL import Image, ImageDraw
import os

def create_square_grid_verification(squares_dir, output_path="square_verification.png"):
    """
    Create a grid showing all extracted squares arranged in their positions.
    """
    # Load metadata
    metadata_path = os.path.join(squares_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata not found at {metadata_path}")
        return
    
    import json
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    square_size = metadata['square_size']
    square_width = square_size['width']
    square_height = square_size['height']
    
    # Create a canvas to display all squares
    # Add some padding between squares
    padding = 2
    canvas_width = (square_width + padding) * 5 + padding
    canvas_height = (square_height + padding) * 5 + padding
    
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Load and place each square
    for row in range(5):
        for col in range(5):
            square_path = os.path.join(squares_dir, f"square_{row}_{col}.png")
            
            if os.path.exists(square_path):
                square = Image.open(square_path)
                
                # Ensure square is correct size
                if square.size != (square_width, square_height):
                    square = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
                    print(f"Warning: square_{row}_{col}.png was {square.size}, resized to ({square_width}, {square_height})")
                
                # Calculate position
                x = padding + col * (square_width + padding)
                y = padding + row * (square_height + padding)
                
                # Paste square
                canvas.paste(square, (x, y))
                
                # Draw border
                draw.rectangle(
                    [x, y, x + square_width, y + square_height],
                    outline='black', width=1
                )
                
                # Add label
                label = f"R{row}C{col}"
                draw.text((x + 5, y + 5), label, fill='red')
            else:
                print(f"Warning: {square_path} not found")
    
    canvas.save(output_path)
    print(f"\nSaved square verification grid: {output_path}")
    print(f"All squares should be {square_width}x{square_height} pixels")
    
    return canvas

def compare_with_original(original_path, squares_dir, output_path="comparison.png"):
    """
    Create a side-by-side comparison of original and reconstructed grid.
    """
    original = Image.open(original_path)
    orig_width, orig_height = original.size
    
    # Load metadata
    metadata_path = os.path.join(squares_dir, "metadata.json")
    import json
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    grid_bounds = metadata['grid_bounds']
    square_size = metadata['square_size']
    
    # Create reconstructed grid
    square_width = square_size['width']
    square_height = square_size['height']
    
    reconstructed = Image.new('RGB', (orig_width, orig_height), 'white')
    
    # Place squares in their positions
    for row in range(5):
        for col in range(5):
            square_path = os.path.join(squares_dir, f"square_{row}_{col}.png")
            if os.path.exists(square_path):
                square = Image.open(square_path)
                if square.size != (square_width, square_height):
                    square = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
                
                x = grid_bounds['left'] + (col * square_width)
                y = grid_bounds['top'] + (row * square_height)
                
                reconstructed.paste(square, (x, y))
    
    # Create side-by-side comparison
    comparison_width = orig_width * 2 + 20
    comparison_height = max(orig_height, reconstructed.height)
    comparison = Image.new('RGB', (comparison_width, comparison_height), 'lightgray')
    
    comparison.paste(original, (0, 0))
    comparison.paste(reconstructed, (orig_width + 20, 0))
    
    # Add labels
    draw = ImageDraw.Draw(comparison)
    draw.text((10, 10), "Original", fill='black')
    draw.text((orig_width + 30, 10), "Reconstructed", fill='black')
    
    comparison.save(output_path)
    print(f"Saved comparison: {output_path}")

if __name__ == "__main__":
    import sys
    
    squares_dir = "squares"
    if len(sys.argv) > 1:
        squares_dir = sys.argv[1]
    
    print("Creating square verification grid...")
    create_square_grid_verification(squares_dir)
    
    if os.path.exists("unnamed.webp"):
        print("\nCreating comparison with original...")
        compare_with_original("unnamed.webp", squares_dir)

