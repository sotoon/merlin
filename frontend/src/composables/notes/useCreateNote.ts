interface CreateNoteResponse extends Note {}

interface CreateNoteError {
  detail?: string;
}

interface CreateNotePayload
  extends Pick<Partial<Note>, 'content' | 'date' | 'title' | 'type'> {
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
