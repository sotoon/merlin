// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  app: {
    head: {
      link: [
        {
          rel: 'stylesheet',
          type: 'text/css',
          href: 'https://fonts.web.sotoon.ir/IRANYekan/fonts.css',
        },
      ],
    },
  },
  modules: ['@nuxtjs/eslint-module', '@nuxtjs/i18n', '@nuxtjs/tailwindcss'],
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

  typescript: {
    shim: false,
    strict: true,
    typeCheck: true,
  },
});
