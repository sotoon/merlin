type GetNoteResponse = Note | null;

interface UseGetNoteOptions {
  id: string;
}

export const useGetNote = ({ id }: UseGetNoteOptions) => {
  return useApiFetch<GetNoteResponse>(`/notes/${id}`);
};
