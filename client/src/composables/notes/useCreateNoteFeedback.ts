interface UsedCreateNoteFeedbackOptions {
  noteId: string;
  owner?: string;
}

interface CreateNoteFeedbackResponse extends NoteFeedback {}

interface CreateNoteFeedbackError {
  detail?: string;
}

interface CreateNoteFeedbackPayload extends Pick<NoteFeedback, 'content'> {
  content: string;
}

export const useCreateNoteFeedback = ({
  noteId,
  owner,
}: UsedCreateNoteFeedbackOptions) =>
  useApiMutation<
    CreateNoteFeedbackResponse,
    CreateNoteFeedbackError,
    CreateNoteFeedbackPayload
  >(`/notes/${noteId}/feedbacks/`, {
    method: 'POST',
    onSuccess: () => {
      refreshNuxtData([
        `note:${noteId}:feedbacks`,
        `note:${noteId}:feedbacks:${owner}`,
      ]);
    },
  });
