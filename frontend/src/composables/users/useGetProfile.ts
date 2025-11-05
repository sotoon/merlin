import { useQuery } from '@tanstack/vue-query';

export const useGetProfile = () => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'Profile'>>({
    queryKey: ['profile'],
    queryFn: () => $api.fetch('/profile/'),
  });
};

export const useGetProfilePermissions = () => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'UserPermissions'>>({
    queryKey: ['profile-permissions'],
    queryFn: () => $api.fetch('/profile/permissions/'),
  });
};
