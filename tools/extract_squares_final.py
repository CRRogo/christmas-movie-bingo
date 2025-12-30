"""
Final square extraction: Extract content INSIDE grid cells, excluding the grid lines themselves.
"""

from PIL import Image, ImageDraw
import os
import json

def detect_grid_lines_accurate(image_path):
    """
    Accurately detect the grid lines that form the bingo card structure.
    Returns the 6 horizontal and 6 vertical lines.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    # Convert to grayscale
    gray = img.convert('L')
    pixels = gray.load()
    
    # Strategy: Look for strong, continuous lines that span most of the grid area
    # These should be the actual grid borders
    
    # Find horizontal lines
    horizontal_candidates = []
    
    # Sample rows and look for dark lines
    for y in range(height):
        dark_pixels = 0
        consecutive_dark = 0
        max_consecutive = 0
        
        # Check a central portion (avoid edges which might have decorations)
        start_x = int(width * 0.1)
        end_x = int(width * 0.9)
        check_width = end_x - start_x
        
        for x in range(start_x, end_x):
            if pixels[x, y] < 180:  # Dark pixel threshold
                dark_pixels += 1
                consecutive_dark += 1
                max_consecutive = max(max_consecutive, consecutive_dark)
            else:
                consecutive_dark = 0
        
        # A grid line should have:
        # - Many dark pixels (> 50% of checked width)
        # - A long consecutive run (> 60% of checked width)
        if dark_pixels > check_width * 0.5 and max_consecutive > check_width * 0.6:
            if not horizontal_candidates or y - horizontal_candidates[-1] > 30:
                horizontal_candidates.append(y)
    
    # Find vertical lines
    vertical_candidates = []
    
    # Check a central portion vertically
    start_y = int(height * 0.15)
    end_y = int(height * 0.85)
    check_height = end_y - start_y
    
    for x in range(width):
        dark_pixels = 0
        consecutive_dark = 0
        max_consecutive = 0
        
        for y in range(start_y, end_y):
            if pixels[x, y] < 180:
                dark_pixels += 1
                consecutive_dark += 1
                max_consecutive = max(max_consecutive, consecutive_dark)
            else:
                consecutive_dark = 0
        
        if dark_pixels > check_height * 0.5 and max_consecutive > check_height * 0.6:
            if not vertical_candidates or x - vertical_candidates[-1] > 30:
                vertical_candidates.append(x)
    
    # Filter to get the 6 lines that form the grid
    def select_best_lines(candidates, min_spacing=80):
        """Select 6 evenly spaced lines."""
        if len(candidates) < 6:
            return None
        
        # Remove lines that are too close together
        filtered = [candidates[0]]
        for c in candidates[1:]:
            if c - filtered[-1] >= min_spacing:
                filtered.append(c)
        
        if len(filtered) < 6:
            return None
        
        # Find the 6 most evenly spaced
        best_set = None
        best_variance = float('inf')
        
        for start in range(len(filtered) - 5):
            test_set = filtered[start:start+6]
            spacings = [test_set[i+1] - test_set[i] for i in range(5)]
            avg = sum(spacings) / len(spacings)
            variance = sum((s - avg) ** 2 for s in spacings) / len(spacings)
            
            if variance < best_variance:
                best_variance = variance
                best_set = test_set
        
        return best_set
    
    h_lines = select_best_lines(horizontal_candidates, min_spacing=100)
    v_lines = select_best_lines(vertical_candidates, min_spacing=80)
    
    # If detection failed, try with lower thresholds
    if not h_lines or not v_lines:
        print("First attempt failed, trying with lower thresholds...")
        # Lower the threshold and try again
        horizontal_candidates = []
        for y in range(height):
            dark_pixels = 0
            consecutive_dark = 0
            max_consecutive = 0
            start_x = int(width * 0.05)
            end_x = int(width * 0.95)
            check_width = end_x - start_x
            
            for x in range(start_x, end_x):
                if pixels[x, y] < 200:
                    dark_pixels += 1
                    consecutive_dark += 1
                    max_consecutive = max(max_consecutive, consecutive_dark)
                else:
                    consecutive_dark = 0
            
            if dark_pixels > check_width * 0.4 and max_consecutive > check_width * 0.5:
                if not horizontal_candidates or y - horizontal_candidates[-1] > 20:
                    horizontal_candidates.append(y)
        
        vertical_candidates = []
        start_y = int(height * 0.1)
        end_y = int(height * 0.9)
        check_height = end_y - start_y
        
        for x in range(width):
            dark_pixels = 0
            consecutive_dark = 0
            max_consecutive = 0
            
            for y in range(start_y, end_y):
                if pixels[x, y] < 200:
                    dark_pixels += 1
                    consecutive_dark += 1
                    max_consecutive = max(max_consecutive, consecutive_dark)
                else:
                    consecutive_dark = 0
            
            if dark_pixels > check_height * 0.4 and max_consecutive > check_height * 0.5:
                if not vertical_candidates or x - vertical_candidates[-1] > 20:
                    vertical_candidates.append(x)
        
        h_lines = select_best_lines(horizontal_candidates, min_spacing=80)
        v_lines = select_best_lines(vertical_candidates, min_spacing=60)
    
    return h_lines, v_lines

def extract_squares_final(image_path, output_dir="squares_final", line_width_estimate=8):
    """
    Extract squares that contain only the content INSIDE grid cells.
    Excludes the grid lines themselves.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Detect grid lines
    print("Detecting grid lines...")
    h_lines, v_lines = detect_grid_lines_accurate(image_path)
    
    if not h_lines or not v_lines:
        print("Error: Could not detect grid lines. Using fallback.")
        # Fallback
        margin_top = int(height * 0.15)
        margin_bottom = int(height * 0.10)
        margin_left = int(width * 0.10)
        margin_right = int(width * 0.10)
        
        grid_height = height - margin_top - margin_bottom
        grid_width = width - margin_left - margin_right
        
        square_height = grid_height // 5
        square_width = grid_width // 5
        
        h_lines = [margin_top + i * square_height for i in range(6)]
        v_lines = [margin_left + i * square_width for i in range(6)]
    
    print(f"Detected horizontal lines: {h_lines}")
    print(f"Detected vertical lines: {v_lines}")
    
    # Calculate square dimensions from spacing between lines
    # We'll use the spacing between lines, but exclude the line width
    h_spacings = [h_lines[i+1] - h_lines[i] for i in range(5)]
    v_spacings = [v_lines[i+1] - v_lines[i] for i in range(5)]
    
    avg_h_spacing = sum(h_spacings) / len(h_spacings)
    avg_v_spacing = sum(v_spacings) / len(v_spacings)
    
    # Estimate line width - grid lines can be several pixels wide
    # Use a much larger buffer to ensure we completely exclude the lines
    # The red lines in the bingo card are the actual grid borders
    # We need to extract content that's well inside, not touching the lines at all
    line_buffer = max(line_width_estimate, 10)  # At least 10 pixels to fully exclude lines
    
    # Square size is the spacing minus the line width on both sides
    # Each cell has a line on the left and right, so we subtract 2*line_buffer
    square_height = int(avg_h_spacing - (2 * line_buffer))
    square_width = int(avg_v_spacing - (2 * line_buffer))
    
    print(f"\nCell spacing: {avg_v_spacing}x{avg_h_spacing}")
    print(f"Line buffer: {line_buffer} pixels on each side")
    print(f"Square size (content only): {square_width}x{square_height}")
    
    print(f"\nAverage spacing: {avg_v_spacing}x{avg_h_spacing}")
    print(f"Square size (excluding lines): {square_width}x{square_height}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create visualization
    vis_img = img.copy()
    draw = ImageDraw.Draw(vis_img)
    
    # Draw detected lines in red
    for y in h_lines:
        draw.line([(v_lines[0], y), (v_lines[-1], y)], fill='red', width=2)
    for x in v_lines:
        draw.line([(x, h_lines[0]), (x, h_lines[-1])], fill='red', width=2)
    
    # Extract squares - content INSIDE the cells, excluding the lines
    squares_info = []
    
    for row in range(5):
        for col in range(5):
            # Extract content INSIDE the cell, excluding the grid lines
            # The grid lines are at v_lines[col] (left edge of cell) and v_lines[col+1] (right edge)
            # We want to extract the content BETWEEN these lines, not including the lines themselves
            
            # Calculate the actual cell boundaries
            # Left edge of cell content: just after the left line
            # Right edge of cell content: just before the right line
            cell_left_line = v_lines[col]
            cell_right_line = v_lines[col + 1]
            cell_top_line = h_lines[row]
            cell_bottom_line = h_lines[row + 1]
            
            # Extract exactly square_width x square_height pixels from INSIDE the cell
            # Start well after the left line to ensure we completely exclude it
            
            # Calculate starting position (well after the left line to exclude it completely)
            # The line is at cell_left_line, we need to start after the line ends
            left = cell_left_line + line_buffer
            top = cell_top_line + line_buffer
            
            # Extract content well inside the cell, far from the grid lines
            # The grid lines are at cell_left_line and cell_right_line
            # We want to start well after the left line and end well before the right line
            
            # For the first column, the left line is the outer border
            # We need to start extraction well after this line to exclude it completely
            if col == 0:
                # Start extraction well after the first line (add extra padding)
                left = cell_left_line + line_buffer + 2
                print(f"First column: line at {cell_left_line}, starting extraction at {left} (total buffer: {line_buffer + 2}px from line)")
            else:
                # For other columns, also ensure we're well past the line
                left = cell_left_line + line_buffer + 1
            
            # For top row, also add extra buffer
            if row == 0:
                top = cell_top_line + line_buffer + 1
            else:
                top = cell_top_line + line_buffer + 1
            
            # Extract exactly the target size (no resizing to avoid squishing)
            right = left + square_width
            bottom = top + square_height
            
            # Ensure we don't go past the cell boundary
            if right > cell_right_line - line_buffer:
                # If we would go past, adjust the start position
                right = cell_right_line - line_buffer
                left = right - square_width
                if left < cell_left_line + line_buffer:
                    # If we can't fit, extract what we can and center it
                    left = cell_left_line + line_buffer
                    right = min(cell_right_line - line_buffer, left + square_width)
            
            if bottom > cell_bottom_line - line_buffer:
                bottom = cell_bottom_line - line_buffer
                top = bottom - square_height
                if top < cell_top_line + line_buffer:
                    top = cell_top_line + line_buffer
                    bottom = min(cell_bottom_line - line_buffer, top + square_height)
            
            # Extract the square content
            square = img.crop((left, top, right, bottom))
            
            # Resize only if necessary (should be rare now)
            if square.size == (square_width, square_height):
                square_resized = square
            else:
                # Only resize if we had to adjust bounds
                square_resized = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
                if col == 0:
                    print(f"Square {row}_{col}: had to resize from {square.size} to {square_width}x{square_height}")
            
            # Save
            square_path = os.path.join(output_dir, f"square_{row}_{col}.png")
            square_resized.save(square_path, "PNG")
            
            squares_info.append({
                'row': row,
                'col': col,
                'extraction_bounds': (left, top, right, bottom),
                'size': (square_width, square_height)
            })
            
            # Draw extraction area in green (what we're actually extracting)
            draw.rectangle([left, top, right, bottom], outline='green', width=1)
    
    # Save visualization
    vis_img.save("grid_final_extraction.png")
    print(f"\nSaved visualization: grid_final_extraction.png")
    print(f"Red lines = detected grid lines")
    print(f"Green boxes = extracted square content (excluding lines)")
    
    # Calculate grid bounds for metadata (the outer boundaries)
    grid_bounds = {
        'top': h_lines[0],
        'bottom': h_lines[-1],
        'left': v_lines[0],
        'right': v_lines[-1]
    }
    
    # Save metadata
    metadata = {
        'square_size': {
            'width': square_width,
            'height': square_height
        },
        'grid_bounds': grid_bounds,
        'grid_lines': {
            'horizontal': h_lines,
            'vertical': v_lines
        },
        'line_buffer': line_buffer,
        'total_squares': len(squares_info),
        'squares': {f"square_{s['row']}_{s['col']}.png": s for s in squares_info}
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nExtracted {len(squares_info)} squares to {output_dir}/")
    print(f"All squares are exactly {square_width}x{square_height} pixels")
    print(f"Content extracted from INSIDE grid cells (excluding grid lines)")
    
    return squares_info, metadata

if __name__ == "__main__":
    import sys
    
    image_path = sys.argv[1] if len(sys.argv) > 1 else "unnamed.webp"
    line_width = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    extract_squares_final(image_path, line_width_estimate=line_width)

