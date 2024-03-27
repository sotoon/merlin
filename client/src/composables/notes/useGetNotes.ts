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
}: UseGetNotesOptions) =>
  useApiFetch<GetNotesResponse>('/notes/', {
    key: 'notes',
    query: {
      type,
      user,
      retrieve_mentions: retrieveMentions,
    },
  });
