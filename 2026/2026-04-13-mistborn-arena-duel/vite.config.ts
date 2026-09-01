import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@game': path.resolve(__dirname, './src/game'),
      '@data': path.resolve(__dirname, './src/data'),
      '@config': path.resolve(__dirname, './src/config'),
    },
  },
});
