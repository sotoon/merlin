export default defineNuxtRouteMiddleware(() => {
  const { $authStore } = useNuxtApp();

  if ($authStore.tokens.refresh) {
    return navigateTo({ name: 'home' });
  }
});
