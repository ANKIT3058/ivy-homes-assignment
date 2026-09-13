import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '')
  // Supports the original local assignment env names while exposing only the
  // VITE names consumed by the browser application.
  return { plugins: [react()], define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || env.IVY_BASE_URL || ''),
    'import.meta.env.VITE_API_KEY': JSON.stringify(env.VITE_API_KEY || env.IVY_API_KEY || ''),
  } }
})
