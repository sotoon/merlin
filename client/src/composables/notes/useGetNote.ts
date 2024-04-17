type GetNoteResponse = Note | null;

interface UseGetNoteOptions {
  id: string;
}

export const useGetNote = ({ id }: UseGetNoteOptions) =>
  useApiFetch<GetNoteResponse>(`/notes/${id}`, { key: `note:${id}` });
