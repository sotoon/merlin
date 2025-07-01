import { useQueryClient } from '@tanstack/vue-query';

interface CreateNoteResponse extends Note {}

interface CreateNoteError {
  detail?: string;
}

interface CreateNotePayload
  extends Pick<
    Partial<Note>,
    | 'title'
    | 'content'
    | 'type'
    | 'mentioned_users'
    | 'linked_notes'
    | 'submit_status'
  > {
  content: string;
  date: string;
  title: string;
}

export const useCreateNote = () => {
  const queryClient = useQueryClient();
  return useApiMutation<CreateNoteResponse, CreateNoteError, CreateNotePayload>(
    '/notes/',
    {
      method: 'POST',
      onSuccess: (note) => {
        queryClient.invalidateQueries({
          predicate: (query) =>
            query.queryKey[0] === 'notes' && query.queryKey[1] === note.type,
        });
      },
    },
  );
};
