# Hallmark Christmas Bingo Generator - Web App

A React + Vite web application that generates randomized bingo cards from your split bingo card assets.

## Features

- 🎲 **Randomized Card Generation**: Click to generate a new randomized bingo card
- 💾 **Download Cards**: Download your generated cards as PNG images
- 🎄 **Festive UI**: Beautiful, modern interface with gradient backgrounds
- ⚡ **Fast**: Built with Vite for lightning-fast development and builds

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Ensure assets are in place:**
   - `public/background_template.png` - The background template with transparent grid
   - `public/squares/square_0_0.png` through `public/squares/square_4_4.png` - All 25 square images

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   The app will be available at `http://localhost:5173` (or the port shown in terminal)

## Usage

1. The app will automatically load all assets and generate an initial card
2. Click **"🎲 Generate New Card"** to create a new randomized bingo card
3. Click **"💾 Download Card"** to save the current card as a PNG image

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to deploy to any static hosting service.

## How It Works

1. Loads the background template image
2. Loads all 25 square images
3. Shuffles all squares except the free space (center square at row 2, col 2)
4. Uses HTML5 Canvas to composite the background and squares into a new bingo card
5. Displays the result and allows downloading

## Project Structure

```
├── public/
│   ├── background_template.png
│   └── squares/
│       ├── square_0_0.png
│       ├── square_0_1.png
│       └── ... (25 total squares)
├── src/
│   ├── components/
│   │   ├── BingoCardGenerator.jsx
│   │   └── BingoCardGenerator.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
└── vite.config.js
```

