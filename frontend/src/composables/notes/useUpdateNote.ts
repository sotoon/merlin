interface UpdateNoteResponse extends Note {}

interface UpdateNoteError {
  detail?: string;
}

interface UpdateNotePayload
  extends Pick<
    Partial<Note>,
    'content' | 'title' | 'mentioned_users' | 'date'
  > {}

interface UseUpdateNoteOptions {
  id: string;
}

export const useUpdateNote = ({ id }: UseUpdateNoteOptions) =>
  useApiMutation<UpdateNoteResponse, UpdateNoteError, UpdateNotePayload>(
    `/notes/${id}/`,
    {
      method: 'PATCH',
      onSuccess: () => {
        refreshNuxtData(`note:${id}`);
      },
    },
  );
