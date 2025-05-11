import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,  // Don't try other ports if 5173 is busy
    hmr: {
      clientPort: 443,  // Critical for Telegram WebView
      protocol: 'wss'   // Required for secure connection
    }
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
    target: 'esnext'
  }
})