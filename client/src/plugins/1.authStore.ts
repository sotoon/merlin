const REFRESH_TOKEN_STORAGE_KEY = 'auth:refresh';

export default defineNuxtPlugin<{ authStore: AuthStore }>(() => {
  const tokens: AuthTokens = {
    access: null,
    refresh: localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY),
  };

  const setTokens = ({ access, refresh }: Partial<AuthTokens>) => {
    if (access) {
      tokens.access = access;
    }

    if (refresh) {
      tokens.refresh = refresh;
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refresh);
    }
  };

  const removeTokens = () => {
    tokens.access = null;
    tokens.refresh = null;
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  };

  const authStore = {
    tokens: tokens as Readonly<AuthTokens>,
    setTokens,
    removeTokens,
  };

  return { provide: { authStore } };
});
