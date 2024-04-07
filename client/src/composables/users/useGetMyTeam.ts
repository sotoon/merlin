type GetMyTeamResponse = User[];

export const useGetMyTeam = (
  fetchOptions?: UseApiFetchOptions<GetMyTeamResponse>,
) =>
  useApiFetch<GetMyTeamResponse>('/my-team/', {
    key: 'my-team',
    ...fetchOptions,
  });
