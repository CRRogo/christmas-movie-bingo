import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/christmas-movie-bingo/' : '/',
  build: {
    assetsDir: 'assets',
    outDir: 'dist',
    // Ensure public folder is copied correctly
    copyPublicDir: true,
  },
  publicDir: 'public',
})

