interface MyFormsResponse {
  my_forms: Form[];
  team_forms: Form[];
}

export const useGetMyForms = () =>
  useApiFetch<MyFormsResponse>('/forms/assigned-by/', {
    key: createNuxtDataKey('my-forms'),
  });
