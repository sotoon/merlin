import { useQuery } from '@tanstack/vue-query';

export const useGetProfile = () => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'Profile'>>({
    queryKey: ['profile'],
    queryFn: () => $api.fetch('/profile/'),
  });
};
