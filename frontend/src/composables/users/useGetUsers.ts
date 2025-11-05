import { useQuery } from '@tanstack/vue-query';

export const useGetUsers = () => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'ProfileList'>[]>({
    queryKey: ['users'],
    queryFn: () => $api.fetch('/users/'),
  });
};

export const useGetUser = (uuid: MaybeRef<string>) => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'Profile'>>({
    queryKey: ['user', uuid],
    queryFn: () => $api.fetch(`/users/${unref(uuid)}/`),
  });
};
