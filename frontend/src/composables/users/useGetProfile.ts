import { useQuery } from '@tanstack/vue-query';

interface GetProfileResponse extends User {}

export const useGetProfile = () => {
  const { $api } = useNuxtApp();

  return useQuery<GetProfileResponse>({
    queryKey: ['profile'],
    queryFn: () => $api.fetch('/profile/'),
  });
};
