import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

interface Error {
  detail?: string;
}
interface UseGetNoteCommentsOptions {
  noteId: string;
  owner?: string;
  enabled?: boolean;
}

export const useGetNoteComments = ({
  noteId,
  owner,
}: UseGetNoteCommentsOptions) => {
  const { $api } = useNuxtApp();

  return useQuery<Schema<'Comment'>[]>({
    queryKey: ['note-comments', noteId, owner],
    queryFn: () =>
      $api.fetch(`/notes/${noteId}/comments/`, { params: { owner } }),
  });
};

export const useCreateNoteComment = (noteId: string) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();

  return useMutation<Schema<'Comment'>, Error, Schema<'CommentRequest'>>({
    mutationFn: (data) =>
      $api.fetch(`/notes/${noteId}/comments/`, { method: 'POST', body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['note-comments', noteId] });
    },
  });
};
