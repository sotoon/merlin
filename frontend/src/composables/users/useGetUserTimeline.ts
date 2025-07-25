import { useInfiniteQuery } from '@tanstack/vue-query';

export const useGetUserTimeline = (userId: MaybeRef<string>) => {
  const { $api } = useNuxtApp();

  return useInfiniteQuery({
    queryKey: ['user-timeline', userId],
    queryFn: ({ pageParam = 1 }) =>
      $api.fetch(`/users/${unref(userId)}/timeline/`, {
        params: {
          include_level: pageParam === 1 ? 'true' : undefined,
          page: pageParam,
        },
      }),
    getNextPageParam: (lastPage) => {
      if (lastPage.next) {
        const url = new URL(lastPage.next);
        const page = url.searchParams.get('page');
        return page ? parseInt(page) : undefined;
      }
      return undefined;
    },
    initialPageParam: 1,
  });
};
