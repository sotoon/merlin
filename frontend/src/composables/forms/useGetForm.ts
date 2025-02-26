export const useGetForm = (formId: string) =>
  useApiFetch<FormDetails>(`/forms/${formId}/`, {
    key: createNuxtDataKey(['form', formId]),
  });
