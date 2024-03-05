import type { FetchError, FetchOptions } from 'ofetch';

interface UseApiMutationOptions extends Omit<FetchOptions<'json'>, 'body'> {
  noAuth?: boolean;
}

interface ExecuteOptions<TResponse, TError> {
  onSuccess?: (response: TResponse) => void;
  onError?: (error: FetchError<TError> | undefined) => void;
}

const useApiMutation = <TResponse, TError, TBody extends FetchOptions['body']>(
  url: string,
  {
    noAuth,
    onSuccess,
    onError,
    ...options
  }: UseApiMutationOptions & ExecuteOptions<TResponse, TError> = {},
) => {
  const { $api } = useNuxtApp();
  const apiFetch = noAuth ? $api.fetchBase : $api.fetch;

  const error = ref<FetchError<TError> | null>();
  const pending = ref(false);

  const execute = ({
    body,
    ...executeOptions
  }: ExecuteOptions<TResponse, TError> & { body?: TBody } = {}) => {
    pending.value = true;
    error.value = null;

    apiFetch<TResponse>(url, {
      ...options,
      body,
    })
      .then((response) => {
        onSuccess?.(response);
        executeOptions.onSuccess?.(response);
      })
      .catch((e) => {
        error.value = e;
        onError?.(e);
        executeOptions.onError?.(e);
      })
      .finally(() => {
        pending.value = false;
      });
  };

  return { execute, error, pending };
};

export default useApiMutation;
