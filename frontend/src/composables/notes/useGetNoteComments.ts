interface UseGetNoteCommentsOptions {
  noteId: string;
  owner?: string;
  enabled?: boolean;
}

export const useGetNoteComments = ({
  noteId,
  owner,
  enabled,
}: UseGetNoteCommentsOptions) =>
  useApiFetch<Schema<'Comment'>[]>(`/notes/${noteId}/comments/`, {
    key: createNuxtDataKey(['note-comments', noteId, owner]),
    query: {
      owner,
    },
    immediate: enabled,
  });
