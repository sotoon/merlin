import introJs from 'intro.js';
import 'intro.js/introjs.css';

export default defineNuxtPlugin((nuxt) => {
  nuxt.vueApp.provide('intro', introJs);
});
