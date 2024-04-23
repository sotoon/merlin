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
    key: createNuxtDataKey(['note-feedbacks', noteId, owner]),
    query: {
      owner,
    },
    immediate: enabled,
  });
