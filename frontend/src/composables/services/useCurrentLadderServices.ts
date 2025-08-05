import { useQuery } from '@tanstack/vue-query';

export const useGetLadders = () => {
  const { $api } = useNuxtApp();
  return useQuery<Schema<'LadderList'>[]>({
    queryKey: ['ladders'],
    queryFn: () => $api.fetch('/ladders/'),
  });
};
