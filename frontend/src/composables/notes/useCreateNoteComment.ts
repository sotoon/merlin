export const useCreateNoteComment = (noteId: string) =>
  useApiMutation<
    Schema<'Comment'>,
    { detail?: string },
    Schema<'CommentRequest'>
  >(`/notes/${noteId}/comments/`, {
    method: 'POST',
    onSuccess: () => {
      invalidateNuxtData(['note-comments', noteId]);
    },
  });
