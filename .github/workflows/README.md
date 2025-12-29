# GitHub Pages Deployment

This workflow automatically deploys the app to GitHub Pages when you push to the main/master branch.

## Setup Instructions

1. **Enable GitHub Pages in your repository:**
   - Go to Settings → Pages
   - Source: Select "GitHub Actions"

2. **Update the base path in `vite.config.js`:**
   - Change `/christmas-movie-bingo/` to match your repository name
   - If your repo is at the root (username.github.io), change it to `/`

3. **Update `package.json` homepage:**
   - Replace `YOUR_USERNAME` with your GitHub username

4. **Push to main/master branch:**
   - The workflow will automatically build and deploy

The app will be available at: `https://YOUR_USERNAME.github.io/christmas-movie-bingo/`

