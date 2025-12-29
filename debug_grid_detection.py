"""
Debug script to detect grid lines in the bingo card and visualize the grid detection.
Uses edge detection to find the actual grid boundaries.
"""

from PIL import Image, ImageDraw, ImageFilter
import os

def detect_grid_lines_pil(image_path):
    """
    Detect grid lines using PIL-only methods.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Convert to grayscale
    gray = img.convert('L')
    
    # Apply edge detection filter
    edges = gray.filter(ImageFilter.FIND_EDGES)
    
    # Create visualization image
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    
    # Get pixel data
    edge_pixels = edges.load()
    gray_pixels = gray.load()
    
    # Threshold for detecting lines (adjust based on your image)
    line_threshold = 100  # Pixels darker than this are considered part of a line
    
    # Detect horizontal lines
    horizontal_lines = []
    # Sample every few rows to find lines
    for y in range(0, height, 2):  # Sample every 2 pixels
        dark_count = 0
        for x in range(width):
            if gray_pixels[x, y] < line_threshold:
                dark_count += 1
        
        # If more than 40% of the row is dark, it might be a line
        if dark_count > width * 0.4:
            # Check neighbors to confirm it's a line
            line_confirmed = True
            for check_y in range(max(0, y-2), min(height, y+3)):
                check_count = sum(1 for x in range(width) if gray_pixels[x, check_y] < line_threshold)
                if check_count < width * 0.3:
                    line_confirmed = False
                    break
            
            if line_confirmed and (not horizontal_lines or abs(y - horizontal_lines[-1]) > 5):
                horizontal_lines.append(y)
                draw.line([(0, y), (width, y)], fill='red', width=2)
    
    # Detect vertical lines
    vertical_lines = []
    for x in range(0, width, 2):  # Sample every 2 pixels
        dark_count = 0
        for y in range(height):
            if gray_pixels[x, y] < line_threshold:
                dark_count += 1
        
        if dark_count > height * 0.4:
            line_confirmed = True
            for check_x in range(max(0, x-2), min(width, x+3)):
                check_count = sum(1 for y in range(height) if gray_pixels[check_x, y] < line_threshold)
                if check_count < height * 0.3:
                    line_confirmed = False
                    break
            
            if line_confirmed and (not vertical_lines or abs(x - vertical_lines[-1]) > 5):
                vertical_lines.append(x)
                draw.line([(x, 0), (x, height)], fill='blue', width=2)
    
    return horizontal_lines, vertical_lines, vis_img

def find_grid_boundaries(horizontal_lines, vertical_lines, width, height):
    """
    Find the actual grid boundaries from detected lines.
    For a 5x5 grid, we expect 6 horizontal lines and 6 vertical lines.
    """
    # Filter and sort lines, remove duplicates
    h_lines = sorted(set(horizontal_lines))
    v_lines = sorted(set(vertical_lines))
    
    print(f"\nDetected {len(h_lines)} unique horizontal lines: {h_lines[:10]}...")
    print(f"Detected {len(v_lines)} unique vertical lines: {v_lines[:10]}...")
    
    # For a 5x5 grid, we need to find 6 evenly spaced lines (top border + 5 dividers)
    # Find the main grid area by looking for the most evenly spaced cluster
    
    # Find the 6 most evenly spaced horizontal lines
    if len(h_lines) >= 6:
        # Try to find a cluster of 6 lines that are roughly evenly spaced
        best_cluster = None
        best_spacing_variance = float('inf')
        
        for i in range(len(h_lines) - 5):
            cluster = h_lines[i:i+6]
            spacings = [cluster[j+1] - cluster[j] for j in range(5)]
            avg_spacing = sum(spacings) / len(spacings)
            variance = sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
            
            if variance < best_spacing_variance:
                best_spacing_variance = variance
                best_cluster = cluster
        
        if best_cluster:
            grid_top = best_cluster[0]
            grid_bottom = best_cluster[-1]
            print(f"Found evenly spaced horizontal lines: {best_cluster}")
        else:
            grid_top = h_lines[0]
            grid_bottom = h_lines[-1]
    else:
        # Fallback: use percentage-based
        grid_top = int(height * 0.15)
        grid_bottom = int(height * 0.90)
        print("Not enough horizontal lines detected, using fallback")
    
    # Same for vertical lines
    if len(v_lines) >= 6:
        best_cluster = None
        best_spacing_variance = float('inf')
        
        for i in range(len(v_lines) - 5):
            cluster = v_lines[i:i+6]
            spacings = [cluster[j+1] - cluster[j] for j in range(5)]
            avg_spacing = sum(spacings) / len(spacings)
            variance = sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
            
            if variance < best_spacing_variance:
                best_spacing_variance = variance
                best_cluster = cluster
        
        if best_cluster:
            grid_left = best_cluster[0]
            grid_right = best_cluster[-1]
            print(f"Found evenly spaced vertical lines: {best_cluster}")
        else:
            grid_left = v_lines[0]
            grid_right = v_lines[-1]
    else:
        grid_left = int(width * 0.10)
        grid_right = int(width * 0.90)
        print("Not enough vertical lines detected, using fallback")
    
    return {
        'top': grid_top,
        'bottom': grid_bottom,
        'left': grid_left,
        'right': grid_right,
        'horizontal_lines': h_lines,
        'vertical_lines': v_lines
    }

def extract_squares_with_debug(image_path, output_dir="debug_squares"):
    """
    Extract squares and create debug visualizations.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Detect grid lines
    print("Detecting grid lines...")
    h_lines, v_lines, vis_img = detect_grid_lines_pil(image_path)
    
    print(f"Found {len(h_lines)} horizontal lines")
    print(f"Found {len(v_lines)} vertical lines")
    
    # Save visualization
    vis_img.save("grid_detection_visualization.png")
    print("Saved grid detection visualization: grid_detection_visualization.png")
    
    # Find grid boundaries
    grid_info = find_grid_boundaries(h_lines, v_lines, width, height)
    
    print(f"\nGrid boundaries:")
    print(f"  Top: {grid_info['top']}")
    print(f"  Bottom: {grid_info['bottom']}")
    print(f"  Left: {grid_info['left']}")
    print(f"  Right: {grid_info['right']}")
    
    grid_width = grid_info['right'] - grid_info['left']
    grid_height = grid_info['bottom'] - grid_info['top']
    
    print(f"\nGrid size: {grid_width}x{grid_height}")
    
    # Calculate square dimensions
    square_width = grid_width // 5
    square_height = grid_height // 5
    
    print(f"Square size: {square_width}x{square_height}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a debug image showing all squares with borders
    debug_img = img.copy()
    debug_draw = ImageDraw.Draw(debug_img)
    
    # Extract and save each square with borders
    squares_info = []
    for row in range(5):
        for col in range(5):
            left = grid_info['left'] + (col * square_width)
            top = grid_info['top'] + (row * square_height)
            right = left + square_width
            bottom = top + square_height
            
            # Draw border on debug image
            debug_draw.rectangle([left, top, right, bottom], outline='red', width=2)
            
            # Extract square
            square = img.crop((left, top, right, bottom))
            
            # Create square with border for debugging
            square_with_border = Image.new('RGB', (square_width + 4, square_height + 4), 'white')
            square_with_border.paste(square, (2, 2))
            border_draw = ImageDraw.Draw(square_with_border)
            border_draw.rectangle([0, 0, square_width + 3, square_height + 3], outline='black', width=2)
            
            # Add label
            label = f"R{row}C{col}"
            border_draw.text((5, 5), label, fill='red')
            
            # Save square
            square_path = os.path.join(output_dir, f"square_{row}_{col}_debug.png")
            square_with_border.save(square_path)
            
            squares_info.append({
                'row': row,
                'col': col,
                'bounds': (left, top, right, bottom),
                'size': (square_width, square_height)
            })
    
    # Save debug image
    debug_img.save("grid_extraction_debug.png")
    print(f"\nSaved debug image: grid_extraction_debug.png")
    print(f"Extracted {len(squares_info)} squares to {output_dir}/")
    
    return squares_info, grid_info

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python debug_grid_detection.py <image_path>")
        print("Example: python debug_grid_detection.py unnamed.webp")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    extract_squares_with_debug(image_path)

