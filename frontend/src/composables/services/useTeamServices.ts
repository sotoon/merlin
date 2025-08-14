import { useQuery } from '@tanstack/vue-query';

export const useGetTeams = () => {
  const { $api } = useNuxtApp();
  return useQuery<Schema<'Team'>[]>({
    queryKey: ['teams'],
    queryFn: () => $api.fetch('/teams/'),
  });
};
