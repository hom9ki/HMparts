import { resolve } from 'path'

export default {
  root: resolve(__dirname, 'src'),
  build: {
    outDir: resolve(__dirname, 'static'),
    cssCodeSplit: true,
    rollupOptions: {
        input: {
            master: resolve(__dirname ,'./src/styles.scss'),
            main: resolve(__dirname, './src/script.js')
        },
        output: {
            assetFileNames: (assetInfo) => {
                if (assetInfo.name.endsWith('.css')) {
                    return '[name][extname]'
                }

                return 'asserts/[name][extname]'
            },
    chunkFileNames: '[name].js]',
    entryFileNames: '[name].js'
  }
  }
  },

  // Optional: Silence Sass deprecation warnings. See note below.
  css: {
     preprocessorOptions: {
        scss: {
          silenceDeprecations: [
            'import',
            'mixed-decls',
            'color-functions',
            'global-builtin',
          ],
        },
     },
  },
}