"""
Advanced script to split a bingo card image into individual squares with interactive calibration.
"""

from PIL import Image, ImageDraw, ImageTk
import os
import sys
import json

try:
    import tkinter as tk
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. Interactive mode disabled.")

def detect_grid_auto(img):
    """
    Attempt to automatically detect the grid boundaries.
    This is a simple heuristic - may need manual adjustment.
    """
    width, height = img.size
    
    # Convert to grayscale for edge detection
    gray = img.convert('L')
    pixels = gray.load()
    
    # Simple approach: look for areas with consistent structure
    # For now, use percentage-based approach with reasonable defaults
    top_margin = int(height * 0.15)
    bottom_margin = int(height * 0.10)
    left_margin = int(width * 0.10)
    right_margin = int(width * 0.10)
    
    return {
        'top': top_margin,
        'bottom': height - bottom_margin,
        'left': left_margin,
        'right': width - right_margin
    }

def split_bingo_card(image_path, output_dir="squares", background_output="background_template.png", 
                     grid_bounds=None, save_config=True):
    """
    Split a bingo card image into 25 individual squares (5x5 grid) and extract the background.
    
    Args:
        image_path: Path to the input bingo card image
        output_dir: Directory to save individual squares
        background_output: Path to save the background template
        grid_bounds: Dict with 'top', 'bottom', 'left', 'right' keys, or None for auto-detect
        save_config: Whether to save the grid bounds to a JSON file for reuse
    """
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Get grid boundaries
    if grid_bounds is None:
        # Try to load from config file first
        config_file = "grid_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                    if image_path in saved_config:
                        grid_bounds = saved_config[image_path]
                        print(f"Loaded grid bounds from config: {grid_bounds}")
            except:
                pass
        
        if grid_bounds is None:
            grid_bounds = detect_grid_auto(img)
            print(f"Auto-detected grid bounds: {grid_bounds}")
    
    grid_top = grid_bounds['top']
    grid_bottom = grid_bounds['bottom']
    grid_left = grid_bounds['left']
    grid_right = grid_bounds['right']
    
    grid_width = grid_right - grid_left
    grid_height = grid_bottom - grid_top
    
    print(f"Grid area: ({grid_left}, {grid_top}) to ({grid_right}, {grid_bottom})")
    print(f"Grid size: {grid_width}x{grid_height}")
    
    # Calculate square dimensions
    square_width = grid_width // 5
    square_height = grid_height // 5
    
    print(f"Square size: {square_width}x{square_height}")
    
    # Create output directory for squares
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract and save each square
    squares = []
    square_data = {}
    for row in range(5):
        for col in range(5):
            # Calculate square boundaries
            left = grid_left + (col * square_width)
            top = grid_top + (row * square_height)
            right = left + square_width
            bottom = top + square_height
            
            # Extract square
            square = img.crop((left, top, right, bottom))
            squares.append(square)
            
            # Save square
            square_filename = f"square_{row}_{col}.png"
            square_path = os.path.join(output_dir, square_filename)
            square.save(square_path, "PNG")
            
            square_data[square_filename] = {
                'row': row,
                'col': col,
                'position': (row, col)
            }
    
    # Save square metadata
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump({
            'square_size': {'width': square_width, 'height': square_height},
            'grid_bounds': grid_bounds,
            'squares': square_data
        }, f, indent=2)
    print(f"Saved metadata: {metadata_path}")
    
    # Create background template
    background = img.copy()
    
    # Create an alpha channel if it doesn't exist
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    
    # Create a mask for the grid area (make it transparent)
    from PIL import ImageDraw
    mask = Image.new('L', background.size, 255)  # White = opaque
    draw = ImageDraw.Draw(mask)
    draw.rectangle([grid_left, grid_top, grid_right, grid_bottom], fill=0)  # Black = transparent
    
    # Apply mask
    background.putalpha(mask)
    
    # Save background template
    background.save(background_output, "PNG")
    print(f"Saved background template: {background_output}")
    
    # Also save a version with white fill for the grid area
    background_white = img.copy()
    if background_white.mode != 'RGB':
        background_white = background_white.convert('RGB')
    draw_white = ImageDraw.Draw(background_white)
    draw_white.rectangle([grid_left, grid_top, grid_right, grid_bottom], fill='white')
    background_white_path = background_output.replace('.png', '_white_fill.png')
    background_white.save(background_white_path, "PNG")
    print(f"Saved background template (white fill): {background_white_path}")
    
    # Save grid bounds to config for reuse
    if save_config:
        config_file = "grid_config.json"
        config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except:
                pass
        config[image_path] = grid_bounds
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Saved grid bounds to: {config_file}")
    
    print(f"\nSuccessfully split bingo card into {len(squares)} squares!")
    print(f"All squares are {square_width}x{square_height} pixels")
    
    return squares, background, square_width, square_height, grid_bounds

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_bingo_card_advanced.py <image_path> [output_dir] [background_output]")
        print("Example: python split_bingo_card_advanced.py bingo_card.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "squares"
    background_output = sys.argv[3] if len(sys.argv) > 3 else "background_template.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    split_bingo_card(image_path, output_dir, background_output)


