"""
Extract squares by detecting the actual grid lines in the bingo card.
Uses a more sophisticated approach to find the 5x5 grid structure.
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import json

def find_grid_lines(image_path):
    """
    Find the actual grid lines by looking for the bingo card structure.
    Returns the 6 horizontal and 6 vertical lines that form the 5x5 grid.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Convert to grayscale
    gray = img.convert('L')
    pixels = gray.load()
    
    # Strategy: Look for lines that span most of the width/height
    # Grid lines should be continuous and relatively straight
    
    # Find horizontal lines (rows)
    horizontal_candidates = []
    
    # Sample rows and look for dark lines
    for y in range(height):
        # Count dark pixels in this row
        dark_count = 0
        consecutive_dark = 0
        max_consecutive = 0
        
        for x in range(width):
            if pixels[x, y] < 200:  # Dark pixel threshold
                dark_count += 1
                consecutive_dark += 1
                max_consecutive = max(max_consecutive, consecutive_dark)
            else:
                consecutive_dark = 0
        
        # A grid line should have:
        # - Many dark pixels (> 30% of width)
        # - A long consecutive run (> 50% of width)
        if dark_count > width * 0.3 and max_consecutive > width * 0.5:
            horizontal_candidates.append(y)
    
    # Find vertical lines (columns)
    vertical_candidates = []
    
    for x in range(width):
        dark_count = 0
        consecutive_dark = 0
        max_consecutive = 0
        
        for y in range(height):
            if pixels[x, y] < 200:
                dark_count += 1
                consecutive_dark += 1
                max_consecutive = max(max_consecutive, consecutive_dark)
            else:
                consecutive_dark = 0
        
        if dark_count > height * 0.3 and max_consecutive > height * 0.5:
            vertical_candidates.append(x)
    
    # Filter candidates to find the 6 lines that form the grid
    # They should be roughly evenly spaced
    
    def filter_close_lines(candidates, min_distance=10):
        """Remove lines that are too close together."""
        if not candidates:
            return []
        
        candidates_sorted = sorted(set(candidates))
        filtered = [candidates_sorted[0]]
        
        for candidate in candidates_sorted[1:]:
            # Only add if it's far enough from the last one
            if candidate - filtered[-1] >= min_distance:
                filtered.append(candidate)
        
        return filtered
    
    def find_best_grid_lines(candidates, total_size, num_lines=6):
        """Find the best set of evenly spaced lines."""
        # First filter out lines that are too close
        candidates_filtered = filter_close_lines(candidates, min_distance=20)
        
        if len(candidates_filtered) < num_lines:
            return None
        
        # Try different starting points
        best_set = None
        best_score = float('inf')
        
        # Try sliding window to find most evenly spaced set
        for start_idx in range(len(candidates_filtered) - num_lines + 1):
            test_set = candidates_filtered[start_idx:start_idx + num_lines]
            
            # Calculate spacing
            spacings = [test_set[i+1] - test_set[i] for i in range(len(test_set)-1)]
            if len(spacings) == 0:
                continue
            
            avg_spacing = sum(spacings) / len(spacings)
            
            # Skip if spacing is too small (probably not a real grid)
            if avg_spacing < total_size * 0.05:
                continue
            
            # Calculate variance (lower is better - more even spacing)
            variance = sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
            
            # Also check that they're in a reasonable area (not all at the edges)
            coverage = (test_set[-1] - test_set[0]) / total_size
            if coverage < 0.3:  # Grid should cover at least 30% of the dimension
                continue
            
            # Prefer sets that are more evenly spaced
            score = variance / (avg_spacing ** 2)  # Normalized variance
            
            if score < best_score:
                best_score = score
                best_set = test_set
        
        return best_set
    
    h_lines = find_best_grid_lines(horizontal_candidates, height, 6)
    v_lines = find_best_grid_lines(vertical_candidates, width, 6)
    
    if not h_lines or not v_lines:
        print("Warning: Could not find 6 evenly spaced lines. Using fallback method.")
        # Fallback: use the first and last candidates and divide evenly
        if horizontal_candidates:
            h_start = min(horizontal_candidates)
            h_end = max(horizontal_candidates)
            h_spacing = (h_end - h_start) / 5
            h_lines = [int(h_start + i * h_spacing) for i in range(6)]
        else:
            h_lines = None
        
        if vertical_candidates:
            v_start = min(vertical_candidates)
            v_end = max(vertical_candidates)
            v_spacing = (v_end - v_start) / 5
            v_lines = [int(v_start + i * v_spacing) for i in range(6)]
        else:
            v_lines = None
    
    return h_lines, v_lines

def extract_squares_using_lines(image_path, output_dir="squares_from_lines"):
    """
    Extract squares using detected grid lines.
    All squares will be exactly the same size.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Find grid lines
    print("Detecting grid lines...")
    h_lines, v_lines = find_grid_lines(image_path)
    
    if not h_lines or not v_lines:
        print("Error: Could not detect grid lines. Please check the image.")
        return None
    
    print(f"Found horizontal lines: {h_lines}")
    print(f"Found vertical lines: {v_lines}")
    
    # Calculate square dimensions from the grid
    # Use the spacing between lines to determine square size
    h_spacings = [h_lines[i+1] - h_lines[i] for i in range(5)]
    v_spacings = [v_lines[i+1] - v_lines[i] for i in range(5)]
    
    # Use the most common spacing (or average)
    square_height = int(sum(h_spacings) / len(h_spacings))
    square_width = int(sum(v_spacings) / len(v_spacings))
    
    print(f"\nCalculated square size: {square_width}x{square_height}")
    
    # Grid boundaries
    grid_top = h_lines[0]
    grid_bottom = h_lines[-1]
    grid_left = v_lines[0]
    grid_right = v_lines[-1]
    
    grid_bounds = {
        'top': grid_top,
        'bottom': grid_bottom,
        'left': grid_left,
        'right': grid_right
    }
    
    print(f"Grid boundaries: top={grid_top}, bottom={grid_bottom}, left={grid_left}, right={grid_right}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualization
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    
    # Draw detected lines
    for y in h_lines:
        draw.line([(grid_left, y), (grid_right, y)], fill='red', width=2)
    for x in v_lines:
        draw.line([(x, grid_top), (x, grid_bottom)], fill='blue', width=2)
    
    # Extract squares - use the line positions to determine boundaries
    squares_info = []
    
    for row in range(5):
        for col in range(5):
            # Use the actual line positions
            left = v_lines[col]
            top = h_lines[row]
            right = v_lines[col + 1]
            bottom = h_lines[row + 1]
            
            # Extract the square
            square = img.crop((left, top, right, bottom))
            
            # Resize to exact size to ensure all squares are equal
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
            
            # Draw border on visualization
            draw.rectangle([left, top, right, bottom], outline='green', width=1)
    
    # Save visualization
    vis_img.save("grid_lines_detection.png")
    print(f"\nSaved grid detection visualization: grid_lines_detection.png")
    
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
    print(f"Saved metadata to {metadata_path}")
    
    return squares_info, metadata, grid_bounds

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_squares_from_lines.py <image_path>")
        print("Example: python extract_squares_from_lines.py unnamed.webp")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    extract_squares_using_lines(image_path)

