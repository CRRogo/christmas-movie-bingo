# Christmas Movie Bingo Generator

A web application for generating randomized Christmas movie bingo cards with interactive gameplay features.

## 🎮 Try It Out

**[Play Now →](https://crrogo.github.io/christmas-movie-bingo/)**

Generate your own personalized bingo cards by entering your name and a movie title!

## 🚀 Running the Web Server

To run the web application locally:

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   The app will be available at `http://localhost:5173` (or the port shown in terminal)

## Project Structure

This repository contains two main components:

### 🎨 Asset Generation Tools (`tools/`)
Python scripts for extracting and processing bingo card assets from source images.

See [`tools/README.md`](tools/README.md) for details on:
- Splitting bingo card images into individual squares
- Extracting background templates
- Grid detection and calibration

### 🌐 Web Application (`src/`, `public/`)
React + Vite web application for generating and playing with bingo cards.

See [`README_WEBAPP.md`](README_WEBAPP.md) for additional details on:
- Building for production
- Deploying to GitHub Pages

## Asset Generation

To extract squares from a bingo card image:

```bash
cd tools
pip install -r requirements.txt
python extract_squares_smart.py
```

## Features

- 🎲 **Deterministic Card Generation**: Same name + movie always generates the same card
- 🎯 **Interactive Gameplay**: Click squares to mark them, automatic bingo detection
- 💾 **Download Cards**: Save cards with QR codes linking back to the game
- 🔗 **Shareable URLs**: Card state encoded in URL for easy sharing
- 🎄 **Festive Design**: Beautiful Christmas-themed UI

## Deployment

The web app is automatically deployed to GitHub Pages on every commit via GitHub Actions.

See `.github/workflows/deploy.yml` for deployment configuration.
