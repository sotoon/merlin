interface DeleteNoteError {
  detail?: string;
}

interface UseDeleteNoteOptions {
  id: string;
}

export const useDeleteNote = ({ id }: UseDeleteNoteOptions) =>
  useApiMutation<never, DeleteNoteError, never>(`/notes/${id}/`, {
    method: 'DELETE',
    onSuccess: () => {
      invalidateNuxtData('notes');
    },
  });
