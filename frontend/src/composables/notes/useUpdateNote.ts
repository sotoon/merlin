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
    | 'year'
    | 'period'
    | 'linked_notes'
  > {}

interface UseUpdateNoteOptions {
  id: string;
}

export const useUpdateNote = ({ id }: UseUpdateNoteOptions) =>
  useApiMutation<UpdateNoteResponse, UpdateNoteError, UpdateNotePayload>(
    `/notes/${id}/`,
    {
      method: 'PATCH',
      onSuccess: (note) => {
        invalidateNuxtData(['note', id]);
        invalidateNuxtData(['notes', note.type]);
      },
    },
  );
