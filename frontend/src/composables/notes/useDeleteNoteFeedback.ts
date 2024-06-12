interface UseDeleteNoteFeedbackOptions {
  noteId: string;
  feedbackId: string;
}

interface DeleteNoteFeedbackError {
  detail?: string;
}

export const useDeleteNoteFeedback = ({
  noteId,
  feedbackId,
}: UseDeleteNoteFeedbackOptions) =>
  useApiMutation<never, DeleteNoteFeedbackError, never>(
    `/notes/${noteId}/feedbacks/${feedbackId}/`,
    {
      method: 'DELETE',
      onSuccess: () => {
        invalidateNuxtData(['note-feedbacks', noteId]);
      },
    },
  );
