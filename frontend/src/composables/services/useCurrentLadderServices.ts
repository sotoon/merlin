import { useQuery } from '@tanstack/vue-query';

export const useGetLadders = () => {
  const { $api } = useNuxtApp();
  return useQuery<Schema<'LadderList'>[]>({
    queryKey: ['ladders'],
    queryFn: () => $api.fetch('/ladders/'),
  });
};

export const useGetLadderByUuid = (uuid: string) => {
  const { $api } = useNuxtApp();
  return useQuery<Schema<'CurrentLadder'>>({
    queryKey: ['ladder', uuid],
    queryFn: () => $api.fetch(`/profile/${uuid}/current-ladder/`),
  });
};
