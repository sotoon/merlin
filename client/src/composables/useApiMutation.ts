import type { FetchError, FetchOptions } from 'ofetch';

interface UseApiMutationOptions extends Omit<FetchOptions<'json'>, 'body'> {
  noAuth?: boolean;
}

interface ExecuteOptions<TResponse, TError>
  extends Omit<FetchOptions<'json'>, 'body'> {
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
    onSuccess: executeOnSuccess,
    onError: executeOnError,
    ...executeOptions
  }: ExecuteOptions<TResponse, TError> & { body?: TBody } = {}) => {
    pending.value = true;
    error.value = null;

    apiFetch<TResponse>(url, {
      ...options,
      ...executeOptions,
      body,
    })
      .then((response) => {
        onSuccess?.(response);
        executeOnSuccess?.(response);
      })
      .catch((e) => {
        error.value = e;
        onError?.(e);
        executeOnError?.(e);
      })
      .finally(() => {
        pending.value = false;
      });
  };

  return { execute, error, pending };
};

export default useApiMutation;
