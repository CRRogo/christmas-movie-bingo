"""
Interactive debug script to manually verify and adjust grid boundaries.
Creates visualizations to help identify the correct grid area.
"""

from PIL import Image, ImageDraw
import os
import json

def create_grid_visualization(image_path, grid_bounds=None):
    """
    Create a visualization showing the grid overlay on the bingo card.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Create visualization
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    
    if grid_bounds is None:
        # Use current metadata values
        grid_bounds = {
            'top': 139,
            'bottom': 834,
            'left': 61,
            'right': 556
        }
    
    # Draw grid overlay
    grid_width = grid_bounds['right'] - grid_bounds['left']
    grid_height = grid_bounds['bottom'] - grid_bounds['top']
    square_width = grid_width // 5
    square_height = grid_height // 5
    
    print(f"\nCurrent grid bounds:")
    print(f"  Top: {grid_bounds['top']}, Bottom: {grid_bounds['bottom']}")
    print(f"  Left: {grid_bounds['left']}, Right: {grid_bounds['right']}")
    print(f"  Grid size: {grid_width}x{grid_height}")
    print(f"  Square size: {square_width}x{square_height}")
    
    # Draw outer border
    draw.rectangle(
        [grid_bounds['left'], grid_bounds['top'], 
         grid_bounds['right'], grid_bounds['bottom']],
        outline='red', width=3
    )
    
    # Draw grid lines
    for i in range(1, 5):
        # Vertical lines
        x = grid_bounds['left'] + (i * square_width)
        draw.line([(x, grid_bounds['top']), (x, grid_bounds['bottom'])], 
                 fill='blue', width=2)
        
        # Horizontal lines
        y = grid_bounds['top'] + (i * square_height)
        draw.line([(grid_bounds['left'], y), (grid_bounds['right'], y)], 
                 fill='blue', width=2)
    
    # Draw each square with label
    for row in range(5):
        for col in range(5):
            left = grid_bounds['left'] + (col * square_width)
            top = grid_bounds['top'] + (row * square_height)
            right = left + square_width
            bottom = top + square_height
            
            # Draw square border
            draw.rectangle([left, top, right, bottom], outline='green', width=1)
            
            # Add label
            label = f"{row},{col}"
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), label)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = left + (square_width - text_width) // 2
            text_y = top + (square_height - text_height) // 2
            
            # Draw text with background
            draw.rectangle(
                [text_x - 2, text_y - 2, text_x + text_width + 2, text_y + text_height + 2],
                fill='white', outline='black'
            )
            draw.text((text_x, text_y), label, fill='black')
    
    return vis_img, grid_bounds, square_width, square_height

def extract_squares_verified(image_path, grid_bounds, square_width, square_height, output_dir="verified_squares"):
    """
    Extract squares using verified grid bounds.
    """
    img = Image.open(image_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    squares_info = []
    
    for row in range(5):
        for col in range(5):
            left = grid_bounds['left'] + (col * square_width)
            top = grid_bounds['top'] + (row * square_height)
            right = left + square_width
            bottom = top + square_height
            
            # Extract square
            square = img.crop((left, top, right, bottom))
            
            # Ensure exact size
            if square.size != (square_width, square_height):
                square = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
            
            # Save
            square_path = os.path.join(output_dir, f"square_{row}_{col}.png")
            square.save(square_path, "PNG")
            
            squares_info.append({
                'row': row,
                'col': col,
                'bounds': (left, top, right, bottom),
                'size': square.size
            })
    
    # Save updated metadata
    metadata = {
        'square_size': {
            'width': square_width,
            'height': square_height
        },
        'grid_bounds': grid_bounds,
        'total_squares': len(squares_info),
        'squares': {f"square_{s['row']}_{s['col']}.png": s for s in squares_info}
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nExtracted {len(squares_info)} squares to {output_dir}/")
    print(f"Saved metadata to {metadata_path}")
    
    return squares_info, metadata

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python debug_grid_manual.py <image_path>")
        print("Example: python debug_grid_manual.py unnamed.webp")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Create visualization
    print("Creating grid visualization...")
    vis_img, grid_bounds, square_width, square_height = create_grid_visualization(image_path)
    
    # Save visualization
    vis_img.save("grid_overlay_visualization.png")
    print("\nSaved grid overlay visualization: grid_overlay_visualization.png")
    print("\nPlease check the visualization to verify the grid is correctly aligned.")
    print("If the grid is misaligned, you can manually adjust the bounds in the script.")
    
    # Extract squares
    print("\nExtracting squares with current bounds...")
    squares_info, metadata = extract_squares_verified(
        image_path, grid_bounds, square_width, square_height
    )
    
    print("\nDone! Check:")
    print("  - grid_overlay_visualization.png (to verify alignment)")
    print("  - verified_squares/ (extracted squares)")

