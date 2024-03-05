import type { UseFetchOptions } from '#app';

import { defu } from 'defu';

interface UseApiFetchOptions<T> extends Omit<UseFetchOptions<T>, '$fetch'> {
  noAuth?: boolean;
}

export function useApiFetch<T>(
  url: string | (() => string),
  { noAuth, ...options }: UseApiFetchOptions<T> = {},
) {
  const { $api } = useNuxtApp();

  const defaults: UseFetchOptions<T> = {
    $fetch: noAuth ? $api.fetchBase : $api.fetch,
  };

  const params = defu(options, defaults);

  return useFetch(url, params);
}
