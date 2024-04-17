interface UpdateProfileResponse extends User {}

interface UpdateProfileError {
  detail?: string;
}

interface UpdateProfilePayload extends ProfileFormValues {}

export const useUpdateProfile = () =>
  useApiMutation<
    UpdateProfileResponse,
    UpdateProfileError,
    UpdateProfilePayload
  >('/profile/', {
    method: 'PATCH',
    onSuccess: () => {
      refreshNuxtData('profile');
    },
  });
