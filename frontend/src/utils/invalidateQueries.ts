import { useQueryClient } from '@tanstack/vue-query';

export function useInvalidateQueries() {
  const queryClient = useQueryClient();

  function invalidateQueries(key: string) {
    queryClient.invalidateQueries({
      predicate: (query) => query.queryKey[0] === key,
    });
  }

  return invalidateQueries;
}
