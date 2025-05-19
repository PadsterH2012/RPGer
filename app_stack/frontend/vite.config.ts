import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import viteTsconfigPaths from 'vite-tsconfig-paths';
import svgr from 'vite-plugin-svgr';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    viteTsconfigPaths(),
    svgr({
      include: '**/*.svg?react',
    }),
  ],
  server: {
    port: 3001,
    open: true,
    host: '0.0.0.0',
  },
  build: {
    outDir: 'build',
  },
  define: {
    // Handle process.env for compatibility with existing code
    'process.env': process.env,
  },
});
