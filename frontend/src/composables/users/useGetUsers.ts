type GetUsersResponse = Pick<User, 'email' | 'name' | 'uuid'>[];

export const useGetUsers = () =>
  useApiFetch<GetUsersResponse>('/users/', {
    key: 'users',
  });
