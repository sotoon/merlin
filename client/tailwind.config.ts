import type { Config } from 'tailwindcss';

import PeyTailwindPreset from '@pey/tailwind-preset';
import Typography from '@tailwindcss/typography';

export default {
  presets: [PeyTailwindPreset],
  content: ['./node_modules/@pey/core/dist/*.{js,css}'],
  theme: {
    container: {
      center: true,
    },
    fontFamily: {
      sans: ['IRANYekan', 'sans-serif'],
      serif: ['IRANYekan', 'serif'],
    },
    extend: {
      fontFamily: {
        'latin-sans': ['sans-serif'],
        'latin-serif': ['serif'],
      },
    },
  },
  plugins: [Typography],
} satisfies Config;
