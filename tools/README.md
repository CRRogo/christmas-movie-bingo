# Christmas Movie Bingo Card Asset Creator

This tool extracts individual square assets from a bingo card image and creates a background template. All squares are exactly the same size, ready for use in the web application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Extract Squares

Extract squares from your bingo card image:

```bash
python extract_squares_smart.py <image_path>
```

### Example:
```bash
python extract_squares_smart.py unnamed.webp
```

This will:
- Create a `squares/` directory with 25 individual square images (named `square_0_0.png` through `square_4_4.png`)
- Save `squares/metadata.json` with square dimensions, grid bounds, and extraction coordinates
- The squares are extracted excluding the red grid lines, with precise boundaries

## Output Structure

After extraction, you'll have:
```
squares/
  ├── square_0_0.png    (top-left)
  ├── square_0_1.png
  ├── ...
  ├── square_4_4.png    (bottom-right)
  └── metadata.json     (square dimensions, grid bounds, and extraction info)
```

## Using the Assets

After extraction, copy the `squares/` folder to:
1. The project root (for development)
2. `public/squares/` (for the web application)

The web application will use these assets to generate randomized bingo cards.

## Features

- **Consistent Square Sizes**: All 25 squares are extracted at exactly the same size
- **Precise Extraction**: Squares exclude grid lines and are extracted with exact boundaries
- **Metadata**: Square positions, dimensions, and extraction bounds saved in JSON
- **Smart Grid Detection**: Uses adaptive buffering to detect grid lines and extract content accurately

