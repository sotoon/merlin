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
    | 'year'
    | 'period'
    | 'linked_notes'
  > {
  content: string;
  date: string;
  title: string;
}

export const useCreateNote = () =>
  useApiMutation<CreateNoteResponse, CreateNoteError, CreateNotePayload>(
    '/notes/',
    {
      method: 'POST',
      onSuccess: (note) => {
        invalidateNuxtData(['notes', note.type]);
      },
    },
  );
