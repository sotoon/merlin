import { PToast } from '@pey/core';

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PToast);
});
