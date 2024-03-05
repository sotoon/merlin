interface GetProfileResponse {
  uuid: string;
  email: string;
  name: string;
  gmail: string;
  phone: string;
  department: string | null;
  chapter: string | null;
  team: string | null;
  leader: string | null;
}

export const useGetProfile = () => {
  return useApiFetch<GetProfileResponse>('/profile/');
};
