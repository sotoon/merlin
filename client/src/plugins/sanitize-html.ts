import sanitizeHtml from 'sanitize-html';

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive<HTMLElement, string>('sanitize-html', {
    mounted(el, binding) {
      el.innerHTML = sanitizeHtml(binding.value, {
        allowedAttributes: {
          a: ['href', 'target', 'rel'],
          '*': ['dir'],
        },
      });
    },
  });
});
