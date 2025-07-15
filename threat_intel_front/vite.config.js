// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8891',
        changeOrigin: true,
        // 不用rewrite
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})