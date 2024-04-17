export const useLogout = () => {
  const { $authStore } = useNuxtApp();

  const logout = () => {
    $authStore.removeTokens();
    window.location.reload();
  };

  return logout;
};
