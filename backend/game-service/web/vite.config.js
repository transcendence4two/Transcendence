import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ws': {
        target: 'http://localhost:8001',
        ws: true,
      },
      '/health': {
        target: 'http://localhost:8001',
      },
    },
    // SPA fallback — serves index.html for all non-file routes like /game/:id
    historyApiFallback: true,
  },
})
