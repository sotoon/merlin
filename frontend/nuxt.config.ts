// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        {
          rel: 'apple-touch-icon',
          sizes: '180x180',
          href: '/apple-touch-icon.png',
        },
        {
          rel: 'icon',
          type: 'image/png',
          sizes: '32x32',
          href: '/favicon-32x32.png',
        },
        {
          rel: 'icon',
          type: 'image/png',
          sizes: '16x16',
          href: '/favicon-16x16.png',
        },
        {
          rel: 'manifest',
          href: '/site.webmanifest',
        },
        {
          rel: 'stylesheet',
          type: 'text/css',
          href: 'https://fonts.web.sotoon.ir/IRANYekan/fonts.css',
        },
      ],
    },
  },
  css: ['~/assets/css/tiptap.scss'],
  imports: {
    dirs: ['composables/**', 'constants', 'types'],
  },
  components: [
    {
      path: '~/components',
    },
    {
      path: '~/components/shared',
      pathPrefix: false,
    },
  ],
  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL,
      bepaAuthUrl: process.env.NUXT_PUBLIC_BEPA_AUTH_URL,
      bepaCallbackUrl: process.env.NUXT_PUBLIC_BEPA_CALLBACK_URL,
      bepaClientId: process.env.NUXT_PUBLIC_BEPA_CLIENT_ID,
    },
  },
  modules: [
    '@nuxtjs/eslint-module',
    '@nuxtjs/i18n',
    '@nuxtjs/tailwindcss',
    '@vee-validate/nuxt',
    'nuxt-tiptap-editor',
  ],
  srcDir: 'src/',
  ssr: false,

  devtools: { enabled: true },

  i18n: {
    locales: [{ code: 'fa', iso: 'fa-IR', dir: 'rtl', file: 'fa.json' }],
    langDir: './locales',
    defaultLocale: 'fa',
    strategy: 'no_prefix',
  },

  tailwindcss: {
    viewer: false,
  },

  tiptap: {
    prefix: 'Tiptap',
  },

  typescript: {
    shim: false,
    strict: true,
    typeCheck: true,
  },

  veeValidate: {
    componentNames: {
      Form: 'VeeForm',
      Field: 'VeeField',
    },
  },
});
