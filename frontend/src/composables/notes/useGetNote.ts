type GetNoteResponse = Note | null;

interface UseGetNoteOptions {
  id: string;
}

export const useGetNote = (
  { id }: UseGetNoteOptions,
  fetchOptions: UseApiFetchOptions<GetNoteResponse> = {},
) =>
  useApiFetch<GetNoteResponse>(`/notes/${id}/`, {
    key: createNuxtDataKey(['note', id]),
    ...fetchOptions,
  });
