type GetNotesResponse = Note[];

interface UseGetNotesOptions {
  type?: NoteType;
  user?: string;
  retrieveMentions?: boolean;
}

export const useGetNotes = (
  { type, user, retrieveMentions }: UseGetNotesOptions = {},
  fetchOptions: UseApiFetchOptions<GetNotesResponse> = {},
) => {
  const transform =
    fetchOptions.transform || ((data: GetNotesResponse) => data);

  return useApiFetch<GetNotesResponse>('/notes/', {
    ...fetchOptions,
    key: createNuxtDataKey(['notes', type, user, retrieveMentions]),
    query: {
      type,
      user,
      retrieve_mentions: retrieveMentions,
    },
    transform: (notes) => transform(notes.map(transformNoteResponse)),
  });
};
