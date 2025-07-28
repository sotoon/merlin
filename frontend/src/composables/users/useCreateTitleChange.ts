import { useMutation, useQueryClient } from '@tanstack/vue-query';

export const useCreateTitleChange = () => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Schema<'TitleChangeRequest'>) =>
      $api.fetch('/title-changes/', {
        method: 'POST',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-timeline'] });
    },
  });
};
