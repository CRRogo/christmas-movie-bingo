"""
Smart square extraction that analyzes pixels to find where grid lines end and content begins.
"""

from PIL import Image, ImageDraw
import os
import json

def find_content_start(pixels, line_pos, direction, search_range, threshold=200):
    """
    Find where content actually starts by analyzing pixel values.
    direction: 'right' or 'down' to search from line position
    """
    if direction == 'right':
        # Search horizontally from line position
        for x in range(line_pos, min(line_pos + search_range, len(pixels[0]))):
            # Check a vertical strip
            dark_count = 0
            for y in range(len(pixels)):
                if pixels[y][x] < threshold:
                    dark_count += 1
            # If less than 30% dark, we've found content area
            if dark_count < len(pixels) * 0.3:
                return x
        return line_pos + search_range // 2
    
    elif direction == 'down':
        # Search vertically from line position
        for y in range(line_pos, min(line_pos + search_range, len(pixels))):
            # Check a horizontal strip
            dark_count = 0
            for x in range(len(pixels[0])):
                if pixels[y][x] < threshold:
                    dark_count += 1
            if dark_count < len(pixels[0]) * 0.3:
                return y
        return line_pos + search_range // 2
    
    return line_pos

def find_content_end(pixels, line_pos, direction, search_range, threshold=200):
    """
    Find where content ends before the next line.
    """
    if direction == 'right':
        # Search backwards from line position
        for x in range(line_pos - 1, max(line_pos - search_range, 0), -1):
            dark_count = 0
            for y in range(len(pixels)):
                if pixels[y][x] < threshold:
                    dark_count += 1
            if dark_count < len(pixels) * 0.3:
                return x + 1
        return line_pos - search_range // 2
    
    elif direction == 'down':
        for y in range(line_pos - 1, max(line_pos - search_range, 0), -1):
            dark_count = 0
            for x in range(len(pixels[0])):
                if pixels[y][x] < threshold:
                    dark_count += 1
            if dark_count < len(pixels[0]) * 0.3:
                return y + 1
        return line_pos - search_range // 2
    
    return line_pos

def extract_squares_smart(image_path, output_dir="squares_smart"):
    """
    Extract squares by intelligently finding content boundaries.
    """
    img = Image.open(image_path)
    width, height = img.size
    
    print(f"Image size: {width}x{height}")
    
    # Convert to grayscale for analysis
    gray = img.convert('L')
    pixel_data = gray.load()  # Access pixels as pixel_data[x, y]
    
    # Use the detected lines from previous extraction
    # These are the grid line positions
    h_lines = [216, 343, 470, 603, 733, 866]
    v_lines = [3, 139, 252, 364, 476, 597]
    
    print(f"Using grid lines:")
    print(f"  Horizontal: {h_lines}")
    print(f"  Vertical: {v_lines}")
    
    # Calculate cell spacing
    h_spacings = [h_lines[i+1] - h_lines[i] for i in range(5)]
    v_spacings = [v_lines[i+1] - v_lines[i] for i in range(5)]
    
    avg_h_spacing = sum(h_spacings) / len(h_spacings)
    avg_v_spacing = sum(v_spacings) / len(v_spacings)
    
    print(f"\nAverage cell spacing: {avg_v_spacing}x{avg_h_spacing}")
    
    # For each cell, find where content actually starts and ends
    # We'll sample a few pixels to determine content boundaries
    
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
    
    squares_info = []
    
    # Determine target square size based on the smallest cell (to avoid cutting off)
    min_cell_width = min(v_spacings)
    min_cell_height = min(h_spacings)
    
    # Use a conservative buffer - find the actual line width by sampling
    # Analyze the first column to find where the line ends
    # Look for the transition from dark (line) to light (content)
    sample_x = v_lines[0]
    line_end_x = sample_x
    
    # Check multiple rows to find consistent line end
    line_end_samples = []
    for sample_y in [h_lines[1], h_lines[2], h_lines[3]]:
        for x in range(sample_x, min(sample_x + 30, width)):
            # Check if this column is mostly light (content area)
            sample_values = [pixel_data[x, y] for y in range(sample_y - 5, sample_y + 5)]
            avg_brightness = sum(sample_values) / len(sample_values)
            if avg_brightness > 180:  # Light area = content
                line_end_samples.append(x)
                break
    
    if line_end_samples:
        line_end_x = max(line_end_samples)  # Use the furthest point to be safe
        line_width_estimate = line_end_x - sample_x
    else:
        line_width_estimate = 8  # Fallback
    
    print(f"Estimated line width: {line_width_estimate} pixels (line ends around x={line_end_x})")
    
    # Use a buffer that ensures we're past the line
    # For first column, use line_end_x as the start, plus 10 more pixels to avoid pulling too far left
    # Then add 2 more pixels, then 2 more pixels to reduce the left side further
    # For other columns, use a standard buffer
    first_col_buffer = line_end_x - v_lines[0] + 2 + 10 + 2 + 2  # Start well after line ends (14px extra total)
    standard_buffer = 6 - 3  # Standard buffer reduced by 3 pixels = 3 pixels
    
    # Calculate square size - use the smallest available space
    # Account for different buffers in first column
    # Buffers are now 3 pixels smaller on all sides
    available_width_first = v_spacings[0] - first_col_buffer - standard_buffer
    available_width_others = min(v_spacings[1:]) - (2 * standard_buffer)
    square_width = int(min(available_width_first, available_width_others))
    
    available_height = min(h_spacings) - (2 * standard_buffer)
    square_height = int(available_height)
    
    print(f"First column buffer: {first_col_buffer} pixels")
    print(f"Standard buffer: {standard_buffer} pixels")
    print(f"Square size: {square_width}x{square_height}")
    
    # Extract squares
    for row in range(5):
        for col in range(5):
            cell_left = v_lines[col]
            cell_right = v_lines[col + 1]
            cell_top = h_lines[row]
            cell_bottom = h_lines[row + 1]
            
            # For the first column, use the calculated line end position
            if col == 0:
                left = v_lines[0] + first_col_buffer
            else:
                left = cell_left + standard_buffer
            
            # For all columns, end before the right line
            right = cell_right - standard_buffer
            
            # For rows, use standard buffer
            top = cell_top + standard_buffer
            bottom = cell_bottom - standard_buffer
            
            # Ensure we have valid bounds
            if right <= left:
                right = left + square_width
            if bottom <= top:
                bottom = top + square_height
            
            # Extract
            square = img.crop((left, top, right, bottom))
            
            # Resize to target size if needed
            if square.size != (square_width, square_height):
                square_resized = square.resize((square_width, square_height), Image.Resampling.LANCZOS)
            else:
                square_resized = square
            
            # Save
            square_path = os.path.join(output_dir, f"square_{row}_{col}.png")
            square_resized.save(square_path, "PNG")
            
            squares_info.append({
                'row': row,
                'col': col,
                'extraction_bounds': (left, top, right, bottom),
                'size': (square_width, square_height)
            })
            
            # Draw extraction area
            draw.rectangle([left, top, right, bottom], outline='green', width=1)
            
            if col == 0:
                print(f"Square {row}_{col}: extracted from ({left},{top}) to ({right},{bottom}), size {square.size}")
    
    vis_img.save("grid_smart_extraction.png")
    print(f"\nSaved visualization: grid_smart_extraction.png")
    
    # Save metadata
    grid_bounds = {
        'top': h_lines[0],
        'bottom': h_lines[-1],
        'left': v_lines[0],
        'right': v_lines[-1]
    }
    
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
        'line_width_estimate': line_width_estimate,
        'first_col_buffer': first_col_buffer,
        'standard_buffer': standard_buffer,
        'total_squares': len(squares_info),
        'squares': {f"square_{s['row']}_{s['col']}.png": s for s in squares_info}
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nExtracted {len(squares_info)} squares to {output_dir}/")
    print(f"All squares are exactly {square_width}x{square_height} pixels")
    
    return squares_info, metadata

if __name__ == "__main__":
    import sys
    
    image_path = sys.argv[1] if len(sys.argv) > 1 else "unnamed.webp"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    extract_squares_smart(image_path)

