import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: '../static',
    emptyOutDir: false,  // Don't empty static dir to preserve downloaded files
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      }
    }
  }
})