"""
Script to create a new bingo card by shuffling and placing squares on the background template.
"""

from PIL import Image
import os
import sys
import json
import random

def create_bingo_card(background_path, squares_dir, output_path, shuffle=True, free_space_row=2, free_space_col=2):
    """
    Create a new bingo card by placing squares on the background template.
    
    Args:
        background_path: Path to the background template (with transparent grid area)
        squares_dir: Directory containing the square images
        output_path: Path to save the new bingo card
        shuffle: Whether to shuffle the squares (except free space)
        free_space_row: Row index for the free space (0-4, default 2 for middle)
        free_space_col: Column index for the free space (0-4, default 2 for middle)
    """
    # Load background
    background = Image.open(background_path).convert('RGBA')
    bg_width, bg_height = background.size
    
    # Load metadata if available
    metadata_path = os.path.join(squares_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            square_size = metadata['square_size']
            grid_bounds = metadata['grid_bounds']
    else:
        # Fallback: assume default grid bounds
        print("Warning: metadata.json not found. Using default grid bounds.")
        grid_bounds = {
            'top': int(bg_height * 0.15),
            'bottom': int(bg_height * 0.90),
            'left': int(bg_width * 0.10),
            'right': int(bg_width * 0.90)
        }
        # Estimate square size
        grid_width = grid_bounds['right'] - grid_bounds['left']
        grid_height = grid_bounds['bottom'] - grid_bounds['top']
        square_size = {
            'width': grid_width // 5,
            'height': grid_height // 5
        }
    
    square_width = square_size['width']
    square_height = square_size['height']
    grid_top = grid_bounds['top']
    grid_left = grid_bounds['left']
    
    # Load all squares
    squares = []
    square_files = []
    for row in range(5):
        for col in range(5):
            square_path = os.path.join(squares_dir, f"square_{row}_{col}.png")
            if os.path.exists(square_path):
                square = Image.open(square_path).convert('RGBA')
                squares.append((square, row, col))
                square_files.append(square_path)
            else:
                print(f"Warning: Square not found: {square_path}")
    
    if len(squares) != 25:
        print(f"Warning: Expected 25 squares, found {len(squares)}")
    
    # Create a list of positions (excluding free space)
    positions = []
    for row in range(5):
        for col in range(5):
            if not (row == free_space_row and col == free_space_col):
                positions.append((row, col))
    
    # Shuffle positions if requested
    if shuffle:
        random.shuffle(positions)
    
    # Create new card
    new_card = background.copy()
    
    # Place squares
    square_idx = 0
    for row in range(5):
        for col in range(5):
            if row == free_space_row and col == free_space_col:
                # Place the free space square (always at position 2,2)
                free_space_square_path = os.path.join(squares_dir, f"square_{free_space_row}_{free_space_col}.png")
                if os.path.exists(free_space_square_path):
                    free_space = Image.open(free_space_square_path).convert('RGBA')
                    x = grid_left + (col * square_width)
                    y = grid_top + (row * square_height)
                    new_card.paste(free_space, (x, y), free_space)
            else:
                # Place a shuffled square
                if square_idx < len(positions):
                    target_row, target_col = positions[square_idx]
                    square_path = os.path.join(squares_dir, f"square_{target_row}_{target_col}.png")
                    if os.path.exists(square_path):
                        square = Image.open(square_path).convert('RGBA')
                        x = grid_left + (col * square_width)
                        y = grid_top + (row * square_height)
                        new_card.paste(square, (x, y), square)
                    square_idx += 1
    
    # Convert to RGB for saving (if needed)
    if new_card.mode == 'RGBA':
        # Create a white background for final image
        final_card = Image.new('RGB', new_card.size, (255, 255, 255))
        final_card.paste(new_card, mask=new_card.split()[3])  # Use alpha channel as mask
        new_card = final_card
    
    # Save the new card
    new_card.save(output_path, "PNG")
    print(f"Created new bingo card: {output_path}")
    
    return new_card

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_bingo_card.py <background_path> <squares_dir> <output_path> [--no-shuffle]")
        print("Example: python create_bingo_card.py background_template.png squares new_card.png")
        sys.exit(1)
    
    background_path = sys.argv[1]
    squares_dir = sys.argv[2]
    output_path = sys.argv[3]
    shuffle = '--no-shuffle' not in sys.argv
    
    if not os.path.exists(background_path):
        print(f"Error: Background template not found: {background_path}")
        sys.exit(1)
    
    if not os.path.exists(squares_dir):
        print(f"Error: Squares directory not found: {squares_dir}")
        sys.exit(1)
    
    create_bingo_card(background_path, squares_dir, output_path, shuffle=shuffle)


