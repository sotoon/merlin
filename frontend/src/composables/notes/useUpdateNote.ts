import { useQueryClient } from '@tanstack/vue-query';

interface UpdateNoteResponse extends Note {}

interface UpdateNoteError {
  detail?: string;
}

interface UpdateNotePayload
  extends Pick<
    Partial<Note>,
    | 'title'
    | 'content'
    | 'mentioned_users'
    | 'date'
    | 'linked_notes'
    | 'submit_status'
  > {}

interface UseUpdateNoteOptions {
  id: string;
}

export const useUpdateNote = ({ id }: UseUpdateNoteOptions) => {
  const queryClient = useQueryClient();
  return useApiMutation<UpdateNoteResponse, UpdateNoteError, UpdateNotePayload>(
    `/notes/${id}/`,
    {
      method: 'PATCH',
      onSuccess: (note) => {
        invalidateNuxtData(['note', id]);
        queryClient.invalidateQueries({
          predicate: (query) =>
            query.queryKey[0] === 'notes' && query.queryKey[1] === note.type,
        });
      },
    },
  );
};
