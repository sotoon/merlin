import { useNuxtApp } from '#app';
import { useQuery } from '@tanstack/vue-query';
import { computed, toValue, type Ref } from 'vue';

export const useGetPerformanceList = (
  params?: Ref<
    Operation<'personnel_performance_table_retrieve'>['parameters']['query']
  >,
) => {
  const { $api } = useNuxtApp();
  const queryKey = computed(() => [
    'personnel-performance-list',
    toValue(params)?.as_of,
    toValue(params)?.csv,
    toValue(params)?.format,
    toValue(params)?.ladder,
    toValue(params)?.ordering,
    toValue(params)?.page,
    toValue(params)?.page_size,
    toValue(params)?.team,
  ]);

  return useQuery<Schema<'PerformanceTableResponse'>>({
    queryKey,
    queryFn: () =>
      $api.fetch('/personnel/performance-table/', { params: toValue(params) }),
  });
};
