"""
Script to split a bingo card image into individual squares and extract the background template.
Creates assets: 25 square images (all the same size) and a background template.
"""

from PIL import Image, ImageDraw
import os
import sys
import json

def split_bingo_card(image_path, output_dir="squares", background_output="background_template.png", 
                     grid_bounds=None):
    """
    Split a bingo card image into 25 individual squares (5x5 grid) and extract the background.
    All squares will be exactly the same size.
    
    Args:
        image_path: Path to the input bingo card image
        output_dir: Directory to save individual squares
        background_output: Path to save the background template
        grid_bounds: Optional dict with 'top', 'bottom', 'left', 'right' keys for manual grid specification
    """
    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Create output directory for squares
    os.makedirs(output_dir, exist_ok=True)
    
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
            # Estimate grid boundaries (percentage-based, can be adjusted)
            top_margin_ratio = 0.15
            bottom_margin_ratio = 0.10
            side_margin_ratio = 0.10
            
            grid_bounds = {
                'top': int(height * top_margin_ratio),
                'bottom': int(height * (1 - bottom_margin_ratio)),
                'left': int(width * side_margin_ratio),
                'right': int(width * (1 - side_margin_ratio))
            }
            print(f"Auto-detected grid bounds: {grid_bounds}")
    
    grid_top = grid_bounds['top']
    grid_bottom = grid_bounds['bottom']
    grid_left = grid_bounds['left']
    grid_right = grid_bounds['right']
    
    grid_width = grid_right - grid_left
    grid_height = grid_bottom - grid_top
    
    print(f"Grid area: ({grid_left}, {grid_top}) to ({grid_right}, {grid_bottom})")
    print(f"Grid size: {grid_width}x{grid_height}")
    
    # Calculate square dimensions - ensure they're exactly divisible
    square_width = grid_width // 5
    square_height = grid_height // 5
    
    # Adjust grid to ensure exact fit (trim any remainder)
    grid_width = square_width * 5
    grid_height = square_height * 5
    grid_right = grid_left + grid_width
    grid_bottom = grid_top + grid_height
    
    print(f"Adjusted square size: {square_width}x{square_height} (exact)")
    print(f"Adjusted grid area: ({grid_left}, {grid_top}) to ({grid_right}, {grid_bottom})")
    
    # Extract and save each square
    squares = []
    square_metadata = {}
    for row in range(5):
        for col in range(5):
            # Calculate square boundaries
            left = grid_left + (col * square_width)
            top = grid_top + (row * square_height)
            right = left + square_width
            bottom = top + square_height
            
            # Extract square
            square = img.crop((left, top, right, bottom))
            
            # Ensure square is exactly the right size (in case of rounding issues)
            if square.size != (square_width, square_height):
                square = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
            
            squares.append(square)
            
            # Save square
            square_filename = f"square_{row}_{col}.png"
            square_path = os.path.join(output_dir, square_filename)
            square.save(square_path, "PNG")
            
            square_metadata[square_filename] = {
                'row': row,
                'col': col,
                'size': {'width': square_width, 'height': square_height},
                'original_position': (row, col)
            }
    
    # Save metadata
    metadata = {
        'square_size': {'width': square_width, 'height': square_height},
        'grid_bounds': grid_bounds,
        'total_squares': len(squares),
        'squares': square_metadata
    }
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata: {metadata_path}")
    
    print(f"\nExtracted {len(squares)} squares, all {square_width}x{square_height} pixels")
    
    # Create background template by removing the grid area
    # Make grid area transparent (useful for overlaying squares later)
    background = img.copy()
    
    # Create an alpha channel if it doesn't exist
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    
    # Create a mask for the grid area
    mask = Image.new('L', background.size, 255)  # White = opaque
    draw = ImageDraw.Draw(mask)
    draw.rectangle([grid_left, grid_top, grid_right, grid_bottom], fill=0)  # Black = transparent
    
    # Apply mask to make grid area transparent
    background.putalpha(mask)
    
    # Save background template
    background.save(background_output, "PNG")
    print(f"Saved background template: {background_output}")
    
    # Also save a version with white fill for the grid area (alternative option)
    background_white = img.copy()
    if background_white.mode != 'RGB':
        background_white = background_white.convert('RGB')
    draw_white = ImageDraw.Draw(background_white)
    draw_white.rectangle([grid_left, grid_top, grid_right, grid_bottom], fill='white')
    background_white_path = background_output.replace('.png', '_white_fill.png')
    background_white.save(background_white_path, "PNG")
    print(f"Saved background template (white fill): {background_white_path}")
    
    # Save grid bounds to config for reuse
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
    
    print(f"\nSuccessfully created all assets!")
    print(f"  - {len(squares)} square images in '{output_dir}/'")
    print(f"  - Background template: '{background_output}'")
    print(f"  - Background template (white fill): '{background_white_path}'")
    print(f"  - All squares are exactly {square_width}x{square_height} pixels")
    
    return squares, background, square_width, square_height

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_bingo_card.py <image_path> [output_dir] [background_output]")
        print("Example: python split_bingo_card.py bingo_card.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "squares"
    background_output = sys.argv[3] if len(sys.argv) > 3 else "background_template.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    split_bingo_card(image_path, output_dir, background_output)


