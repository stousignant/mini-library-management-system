import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  test: {
    globals: true,
    environment: 'jsdom'
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling:
        process.env.VITE_USE_FILE_POLLING === 'true' ||
        process.env.USE_FILE_POLLING === 'true',
      interval: 1000
    }
  }
})
