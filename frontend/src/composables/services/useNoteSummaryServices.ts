import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

interface Error {
  detail?: string;
}

interface UseGetNoteSummariesOptions {
  noteId: string;
  enabled?: boolean;
}

export const useGetNoteSummaries = ({ noteId }: UseGetNoteSummariesOptions) => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'Summary'>[]>({
    queryKey: ['note-summaries', noteId],
    queryFn: () => $api.fetch(`/notes/${noteId}/summaries/`),
  });
};

export const useCreateNoteSummary = (noteId: string) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();

  return useMutation<Schema<'Summary'>, Error, Schema<'SummaryRequest'>>({
    mutationFn: (data) =>
      $api.fetch(`/notes/${noteId}/summaries/`, { method: 'POST', body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['note-summaries', noteId] });
    },
  });
};
