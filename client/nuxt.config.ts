// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/eslint-module', '@nuxtjs/i18n'],
  srcDir: 'src/',
  ssr: false,

  devtools: { enabled: true },

  i18n: {
    locales: [{ code: 'fa', iso: 'fa-IR', dir: 'rtl', file: 'fa.json' }],
    langDir: './locales',
    defaultLocale: 'fa',
    strategy: 'no_prefix',
  },

  typescript: {
    shim: false,
    strict: true,
    typeCheck: true,
  },
});
