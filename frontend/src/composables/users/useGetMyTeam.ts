export const useGetMyTeam = (
  fetchOptions?: UseApiFetchOptions<Schema<'Profile'>[]>,
) =>
  useApiFetch<Schema<'Profile'>[]>('/my-team/', {
    key: 'my-team',
    dedupe: 'defer',
    ...fetchOptions,
  });
