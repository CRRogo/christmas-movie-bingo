"""
More robust square extraction by analyzing the actual grid structure.
Looks for the rectangular grid area and divides it evenly.
"""

from PIL import Image, ImageDraw
import os
import json

def analyze_image_structure(image_path):
    """
    Analyze the image to find the grid area by looking for rectangular structures.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Convert to grayscale
    gray = img.convert('L')
    pixels = gray.load()
    
    # Strategy: Find the main rectangular grid area
    # Look for areas with consistent structure (the grid cells)
    
    # Sample the image to find the grid area
    # The grid should be in the middle portion, not at the very edges
    
    # Try to find horizontal boundaries by looking for areas with less variation
    # Grid area should have more structure (lines) than decorative areas
    
    # Simple approach: Use the middle 70% of the image as the likely grid area
    # Then look for the actual grid boundaries within that area
    
    margin_top = int(height * 0.15)
    margin_bottom = int(height * 0.10)
    margin_left = int(width * 0.10)
    margin_right = int(width * 0.10)
    
    search_top = margin_top
    search_bottom = height - margin_bottom
    search_left = margin_left
    search_right = width - margin_right
    
    # Within the search area, find the actual grid by looking for the most structured region
    # The grid should have clear horizontal and vertical divisions
    
    # Find horizontal grid lines by looking for rows with many edge transitions
    horizontal_lines = []
    for y in range(search_top, search_bottom):
        edge_count = 0
        for x in range(search_left, search_right - 1):
            # Count significant brightness changes (edges)
            if abs(pixels[x, y] - pixels[x+1, y]) > 30:
                edge_count += 1
        
        # Grid lines should have many edges
        if edge_count > (search_right - search_left) * 0.4:
            if not horizontal_lines or y - horizontal_lines[-1] > 20:  # Min distance
                horizontal_lines.append(y)
    
    # Find vertical grid lines
    vertical_lines = []
    for x in range(search_left, search_right):
        edge_count = 0
        for y in range(search_top, search_bottom - 1):
            if abs(pixels[x, y] - pixels[x, y+1]) > 30:
                edge_count += 1
        
        if edge_count > (search_bottom - search_top) * 0.4:
            if not vertical_lines or x - vertical_lines[-1] > 20:
                vertical_lines.append(x)
    
    # Filter to get 6 lines (for 5x5 grid)
    def select_grid_lines(lines, min_spacing=50):
        if len(lines) < 6:
            return None
        
        # Group lines that are close together
        groups = []
        current_group = [lines[0]]
        
        for line in lines[1:]:
            if line - current_group[-1] < min_spacing:
                current_group.append(line)
            else:
                groups.append(current_group)
                current_group = [line]
        groups.append(current_group)
        
        # From each group, pick the middle line (or average)
        selected = []
        for group in groups:
            selected.append(int(sum(group) / len(group)))
        
        # If we have more than 6, try to pick the 6 most evenly spaced
        if len(selected) >= 6:
            # Find the best 6 that are evenly spaced
            best_set = None
            best_variance = float('inf')
            
            for start in range(len(selected) - 5):
                test_set = selected[start:start+6]
                spacings = [test_set[i+1] - test_set[i] for i in range(5)]
                avg = sum(spacings) / len(spacings)
                variance = sum((s - avg) ** 2 for s in spacings) / len(spacings)
                
                if variance < best_variance:
                    best_variance = variance
                    best_set = test_set
            
            return best_set if best_set else selected[:6]
        
        return selected[:6] if len(selected) >= 6 else None
    
    h_lines = select_grid_lines(horizontal_lines, min_spacing=80)
    v_lines = select_grid_lines(vertical_lines, min_spacing=80)
    
    return h_lines, v_lines, (search_top, search_bottom, search_left, search_right)

def extract_squares_robust(image_path, output_dir="squares_robust"):
    """
    Extract squares using robust grid detection.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Analyze structure
    print("Analyzing image structure...")
    h_lines, v_lines, search_area = analyze_image_structure(image_path)
    
    if not h_lines or not v_lines:
        print("Could not detect grid lines automatically.")
        print("Using fallback: dividing middle area into 5x5 grid")
        
        # Fallback: use percentage-based with the search area
        search_top, search_bottom, search_left, search_right = search_area
        
        grid_height = search_bottom - search_top
        grid_width = search_right - search_left
        
        square_height = grid_height // 5
        square_width = grid_width // 5
        
        # Adjust to exact multiples
        grid_height = square_height * 5
        grid_width = square_width * 5
        
        # Center the grid in the search area
        grid_top = search_top + (search_bottom - search_top - grid_height) // 2
        grid_left = search_left + (search_right - search_left - grid_width) // 2
        grid_bottom = grid_top + grid_height
        grid_right = grid_left + grid_width
        
        h_lines = [grid_top + i * square_height for i in range(6)]
        v_lines = [grid_left + i * square_width for i in range(6)]
        
        print(f"Using fallback grid: top={grid_top}, left={grid_left}")
        print(f"Square size: {square_width}x{square_height}")
    
    print(f"Horizontal lines: {h_lines}")
    print(f"Vertical lines: {v_lines}")
    
    # Calculate square size from line spacing
    h_spacings = [h_lines[i+1] - h_lines[i] for i in range(5)]
    v_spacings = [v_lines[i+1] - v_lines[i] for i in range(5)]
    
    square_height = int(sum(h_spacings) / len(h_spacings))
    square_width = int(sum(v_spacings) / len(v_spacings))
    
    print(f"\nSquare size: {square_width}x{square_height}")
    
    grid_bounds = {
        'top': h_lines[0],
        'bottom': h_lines[-1],
        'left': v_lines[0],
        'right': v_lines[-1]
    }
    
    print(f"Grid bounds: {grid_bounds}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualization
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    
    # Draw grid
    for y in h_lines:
        draw.line([(v_lines[0], y), (v_lines[-1], y)], fill='red', width=2)
    for x in v_lines:
        draw.line([(x, h_lines[0]), (x, h_lines[-1])], fill='blue', width=2)
    
    # Extract squares
    squares_info = []
    
    for row in range(5):
        for col in range(5):
            left = v_lines[col]
            top = h_lines[row]
            right = v_lines[col + 1]
            bottom = h_lines[row + 1]
            
            # Extract
            square = img.crop((left, top, right, bottom))
            
            # Resize to exact size
            square_resized = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
            
            # Save
            square_path = os.path.join(output_dir, f"square_{row}_{col}.png")
            square_resized.save(square_path, "PNG")
            
            squares_info.append({
                'row': row,
                'col': col,
                'original_bounds': (left, top, right, bottom),
                'size': (square_width, square_height)
            })
            
            # Draw border
            draw.rectangle([left, top, right, bottom], outline='green', width=1)
    
    vis_img.save("grid_robust_detection.png")
    print(f"\nSaved visualization: grid_robust_detection.png")
    
    # Save metadata
    metadata = {
        'square_size': {
            'width': square_width,
            'height': square_height
        },
        'grid_bounds': grid_bounds,
        'detected_lines': {
            'horizontal': h_lines,
            'vertical': v_lines
        },
        'total_squares': len(squares_info),
        'squares': {f"square_{s['row']}_{s['col']}.png": s for s in squares_info}
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Extracted {len(squares_info)} squares to {output_dir}/")
    print(f"All squares are exactly {square_width}x{square_height} pixels")
    
    return squares_info, metadata

if __name__ == "__main__":
    import sys
    
    image_path = sys.argv[1] if len(sys.argv) > 1 else "unnamed.webp"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    extract_squares_robust(image_path)

