interface RenewTokenResponse {
  access: string;
}

export const useRenewToken = () => {
  const { $authStore } = useNuxtApp();
  const config = useRuntimeConfig();
  const logout = useLogout();

  const renewToken = () =>
    $fetch<RenewTokenResponse>('/login/refresh/', {
      baseURL: config.public.apiUrl,
      method: 'POST',
      body: { refresh: $authStore.tokens.refresh },
    })
      .then((newToken) => {
        $authStore.setTokens({ access: newToken.access });

        return newToken;
      })
      .catch((error) => {
        if (error?.response?.status === 401) {
          logout();
        }
      });

  return useAsyncData('auth:refresh', renewToken, {
    immediate: false,
    dedupe: 'defer',
  });
};
