import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api/agent':      { target: 'http://localhost:8001', changeOrigin: true, rewrite: p => p.replace(/^\/api\/agent/, '') },
      '/api/blockchain': { target: 'http://localhost:8000', changeOrigin: true, rewrite: p => p.replace(/^\/api\/blockchain/, '') },
      '/api/ml':         { target: 'http://localhost:8002', changeOrigin: true, rewrite: p => p.replace(/^\/api\/ml/, '') },
      '/api/cyber':      { target: 'http://localhost:8003', changeOrigin: true, rewrite: p => p.replace(/^\/api\/cyber/, '') },
    }
  }
})
