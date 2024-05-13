import { ofetch } from 'ofetch';

export default defineNuxtPlugin((nuxtApp) => {
  const $authStore = nuxtApp.$authStore as AuthStore;

  const { execute: renewToken } = useRenewToken();
  const logout = useLogout();

  const apiFetchBase = ofetch.create({
    baseURL: nuxtApp.$config.public.apiUrl,
  });

  const apiFetch = apiFetchBase.create({
    retryStatusCodes: [401],
    async onRequest({ options }) {
      const abortController = new AbortController();
      options.signal = abortController.signal;

      if (!$authStore.tokens.refresh) {
        abortController.abort();
        logout();

        return;
      }

      if (!$authStore.tokens.access) {
        await renewToken();
      }

      if ($authStore.tokens.access) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${$authStore.tokens.access}`,
        };
      } else {
        abortController.abort();
        logout();
      }
    },
    async onResponseError({ response, options }) {
      if (response.status !== 401) {
        return;
      }

      await renewToken();

      if (!options.retry) {
        options.retry = 1;
      }

      options.onResponseError = () => {
        logout();
      };
    },
  });

  const api = {
    fetch: apiFetch,
    fetchBase: apiFetchBase,
  };

  return { provide: { api: api as Readonly<typeof api> } };
});
