import { useToast } from '@pey/core';

interface LoginResponse {
  email: string;
  name: string;
  tokens: {
    access: string;
    refresh: string;
  };
}

interface LoginError {
  detail?: string;
}

interface LoginPayload {
  email: string;
  password: string;
}

export const useLogin = () => {
  const { $authStore } = useNuxtApp();
  const { t } = useI18n();
  const toast = useToast();

  return useApiMutation<LoginResponse, LoginError, LoginPayload>('/login/', {
    method: 'POST',
    noAuth: true,
    onSuccess: ({ tokens }) => {
      $authStore.setTokens(tokens);
      navigateTo('/', { replace: true });
    },
    onError: (error) => {
      toast.error({
        title: t('login.loginFailed'),
        message: error?.response?._data?.detail || '',
      });
    },
  });
};
