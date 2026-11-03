import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// base './' keeps the build working from any folder or sub-path on a static host.
export default defineConfig({
  base: './',
  plugins: [vue()],
  test: { environment: 'node', include: ['tests/**/*.spec.js'] }
});
