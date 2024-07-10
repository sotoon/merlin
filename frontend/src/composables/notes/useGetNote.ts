type GetNoteResponse = Note;

interface UseGetNoteOptions {
  id: string;
}

export const useGetNote = (
  { id }: UseGetNoteOptions,
  fetchOptions: UseApiFetchOptions<GetNoteResponse> = {},
) =>
  useApiFetch<GetNoteResponse>(`/notes/${id}/`, {
    ...fetchOptions,
    key: createNuxtDataKey(['note', id]),
    transform: transformNoteResponse,
  });
