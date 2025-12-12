import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Use IPv4 loopback to avoid environments where localhost resolves to ::1 only
      '/api': 'http://127.0.0.1:8000'
    }
  }
})
