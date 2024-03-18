type GetNotesResponse = Note[];

interface UseGetNotesOptions {
  type?: NoteType;
  user?: string;
  retrieveMentions?: boolean;
}

export const useGetNotes = ({
  type,
  user,
  retrieveMentions,
}: UseGetNotesOptions) => {
  return useApiFetch<GetNotesResponse>('/notes/', {
    query: {
      type,
      user,
      retrieve_mentions: retrieveMentions,
    },
  });
};
