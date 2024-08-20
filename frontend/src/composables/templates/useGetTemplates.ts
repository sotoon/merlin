type GetTemplatesResponse = Note[];

export const useGetTemplates = () =>
  useApiFetch<GetTemplatesResponse>('/templates/', {
    key: 'templates'
  });
