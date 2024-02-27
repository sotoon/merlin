// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/eslint-module'],
  srcDir: 'src/',
  ssr: false,

  devtools: { enabled: true },

  typescript: {
    shim: false,
    strict: true,
    typeCheck: true,
  },
});
