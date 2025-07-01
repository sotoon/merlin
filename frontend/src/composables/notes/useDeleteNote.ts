import { useQueryClient } from '@tanstack/vue-query';

interface DeleteNoteError {
  detail?: string;
}

interface UseDeleteNoteOptions {
  id: string;
}

export const useDeleteNote = ({ id }: UseDeleteNoteOptions) => {
  const queryClient = useQueryClient();
  return useApiMutation<never, DeleteNoteError, never>(`/notes/${id}/`, {
    method: 'DELETE',
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => query.queryKey[0] === 'notes',
      });
    },
  });
};
