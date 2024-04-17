type GetUsersResponse = User[];

export const useGetUsers = () =>
  useApiFetch<GetUsersResponse>('/users/', {
    key: 'users',
  });
