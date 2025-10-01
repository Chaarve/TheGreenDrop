import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://thegreendrop-backend.onrender.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Fallback proxies in case frontend calls bare paths without /api
      '/weather': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/predict': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/health': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/predictions': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/dashboard': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/analytics': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true },
      '/export': { target: 'https://thegreendrop-backend.onrender.com', changeOrigin: true }
    }
  }
})
