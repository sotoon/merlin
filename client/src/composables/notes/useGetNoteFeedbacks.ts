type GetNoteFeedbacksResponse = NoteFeedback[];

interface UseGetNoteFeedbacksOptions {
  noteId: string;
  owner?: string;
  enabled?: boolean;
}

export const useGetNoteFeedbacks = ({
  noteId,
  owner,
  enabled,
}: UseGetNoteFeedbacksOptions) =>
  useApiFetch<GetNoteFeedbacksResponse>(`/notes/${noteId}/feedbacks/`, {
    key: owner
      ? `note:${noteId}:feedbacks:${owner}`
      : `note:${noteId}:feedbacks`,
    query: {
      owner,
    },
    immediate: enabled,
  });
