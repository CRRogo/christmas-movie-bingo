# Christmas Movie Bingo Card Asset Creator

This tool splits a bingo card image into individual square assets and extracts the background template. All squares are exactly the same size, ready for programmatic use.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Step 1: Split the Bingo Card

Split your original bingo card image into individual squares:

### Basic Version:
```bash
python split_bingo_card.py <image_path> [output_dir] [background_output]
```

### Advanced Version (with config saving):
```bash
python split_bingo_card_advanced.py <image_path> [output_dir] [background_output]
```

### Example:
```bash
python split_bingo_card_advanced.py bingo_card.png
```

This will:
- Create a `squares/` directory with 25 individual square images (named `square_0_0.png` through `square_4_4.png`)
- Save `background_template.png` (with transparent grid area)
- Save `background_template_white_fill.png` (with white-filled grid area)
- Save `squares/metadata.json` with square dimensions and grid bounds (advanced version)
- Save `grid_config.json` for reuse with the same image (advanced version)


## Output Structure

After splitting, you'll have:
```
squares/
  ├── square_0_0.png    (top-left)
  ├── square_0_1.png
  ├── ...
  ├── square_4_4.png    (bottom-right)
  └── metadata.json     (square dimensions and grid info)

background_template.png          (transparent grid area)
background_template_white_fill.png  (white-filled grid area)
grid_config.json                 (saved grid bounds for reuse)
```

## Grid Detection

The scripts use percentage-based margins to detect the grid area. If your bingo card has a different layout, you may need to adjust the margin ratios in the script:
- `top_margin_ratio`: Top margin (default: 0.15)
- `bottom_margin_ratio`: Bottom margin (default: 0.10)
- `side_margin_ratio`: Left/right margins (default: 0.10)

The advanced version saves these bounds to `grid_config.json` so you don't need to recalibrate for the same image.

## Features

- **Consistent Square Sizes**: All 25 squares are extracted at exactly the same size
- **Background Template**: Separate background image with transparent grid area, ready for populating with squares
- **Metadata**: Square positions and dimensions saved in JSON for programmatic use
- **Config Saving**: Grid bounds are saved for reuse with the same image
- **Exact Dimensions**: Grid is adjusted to ensure perfect 5x5 division with no remainder

