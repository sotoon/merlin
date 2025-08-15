import { useNuxtApp } from '#app';
import { useQuery } from '@tanstack/vue-query';

export function useGetPerformanceList(
  params: MaybeRef<Record<string, string | number | undefined>>,
) {
  const { $api } = useNuxtApp();
  const queryKey = computed(() => ['personnel-performance-list', params]);

  return useQuery<Schema<'PerformanceTableResponse'>>({
    queryKey,
    queryFn: () =>
      $api.fetch('/personnel/performance-table/', { params: toValue(params) }),
  });
}
