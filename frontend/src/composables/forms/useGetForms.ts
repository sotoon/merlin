export const useGetForms = () =>
  useApiFetch<FormResponse>('/forms/', {
    key: createNuxtDataKey('forms'),
    transform: (data) => {
      data.active_forms.sort((a) => (a.is_filled ? 1 : -1));
      return data;
    },
  });
