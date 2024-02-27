import type { Config } from 'tailwindcss';

import PeyTailwindPreset from '@pey/tailwind-preset';

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
  },
} satisfies Config;
