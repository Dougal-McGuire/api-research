import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  build: {
    outDir: '../static',
    emptyOutDir: true,
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