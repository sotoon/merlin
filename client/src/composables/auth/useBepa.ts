import { useToast } from '@pey/core';

export const useBepaLogin = () => {
  const config = useRuntimeConfig();

  const handleBepaLogin = () => {
    const baseAuthUrl = config.public.bepaAuthUrl;
    const clientId = encodeURIComponent(config.public.bepaClientId);
    const callbackUrl = encodeURIComponent(config.public.bepaCallbackUrl);

    const stateValue = Math.random().toString(36).substring(7);
    sessionStorage.setItem('stateValue', stateValue);

    const bepaAuthUrl = `${baseAuthUrl}/?next=/openid-v2/authorize/%3Fclient_id%3D${clientId}%26redirect_uri%3D${callbackUrl}%26response_type%3Dcode%26scope%3Daddress%2Bphone%2Bopenid%2Bprofile%2Bemail%26state%3D${stateValue}%26`;
    window.location.href = bepaAuthUrl;
  };

  return handleBepaLogin;
};

interface BepaCallbackResponse {
  access: string;
  refresh: string;
}

// TODO: complete this type
interface BepaCallbackError {}

export const useBepaCallback = () => {
  const { t } = useI18n();
  const { $authStore } = useNuxtApp();
  const toast = useToast();

  return useApiMutation<BepaCallbackResponse, BepaCallbackError, never>(
    '/bepa-callback/',
    {
      noAuth: true,
      onSuccess: (tokens) => {
        $authStore.setTokens(tokens);
      },
      onError: () => {
        toast.error({ title: t('login.connectingToBepaFailed'), message: '' });
      },
    },
  );
};
