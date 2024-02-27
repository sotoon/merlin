import type { Config } from 'tailwindcss';

import PeyTailwindPreset from '@pey/tailwind-preset';

export default {
  presets: [PeyTailwindPreset],
  content: [],
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
