interface GetProfileResponse extends User {}

export const useGetProfile = () => {
  return useApiFetch<GetProfileResponse>('/profile/');
};
