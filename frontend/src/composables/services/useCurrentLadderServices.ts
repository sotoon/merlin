import { useQuery } from '@tanstack/vue-query';

export const useGetCurrentLadder = (userUuid?: string) => {
  const { $api } = useNuxtApp();

  const endpoint = userUuid
    ? `/profile/${userUuid}/current-ladder/`
    : '/profile/current-ladder/';

  return useQuery<Schema<'CurrentLadder'>>({
    queryKey: ['current-ladder', userUuid],
    queryFn: () => $api.fetch(endpoint),
  });
};
