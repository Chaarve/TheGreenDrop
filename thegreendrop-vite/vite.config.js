import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Fallback proxies in case frontend calls bare paths without /api
      '/weather': { target: 'http://localhost:5000', changeOrigin: true },
      '/predict': { target: 'http://localhost:5000', changeOrigin: true },
      '/health': { target: 'http://localhost:5000', changeOrigin: true },
      '/predictions': { target: 'http://localhost:5000', changeOrigin: true },
      '/dashboard': { target: 'http://localhost:5000', changeOrigin: true },
      '/analytics': { target: 'http://localhost:5000', changeOrigin: true },
      '/export': { target: 'http://localhost:5000', changeOrigin: true }
    }
  }
})
