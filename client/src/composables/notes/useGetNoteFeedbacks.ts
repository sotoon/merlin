type GetNoteFeedbacksResponse = NoteFeedback[];

interface UseGetNoteFeedbacksOptions {
  noteId: string;
  owner?: string;
}

export const useGetNoteFeedbacks = ({
  noteId,
  owner,
}: UseGetNoteFeedbacksOptions) =>
  useApiFetch<GetNoteFeedbacksResponse>(`/notes/${noteId}/feedbacks/`, {
    key: `note:${noteId}:feedbacks`,
    query: {
      owner,
    },
  });
