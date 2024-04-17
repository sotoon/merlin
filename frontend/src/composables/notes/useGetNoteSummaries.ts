type GetNoteSummariesResponse = NoteSummary[];

interface UseGetNoteSummariesOptions {
  noteId: string;
}

export const useGetNoteSummaries = ({ noteId }: UseGetNoteSummariesOptions) =>
  useApiFetch<GetNoteSummariesResponse>(`/notes/${noteId}/summaries/`, {
    key: `note:${noteId}:summaries`,
  });
