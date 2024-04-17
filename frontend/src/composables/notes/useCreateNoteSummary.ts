interface UsedCreateNoteSummaryOptions {
  noteId: string;
}

interface CreateNoteSummaryResponse extends NoteFeedback {}

interface CreateNoteSummaryError {
  detail?: string;
}

interface CreateNoteSummaryPayload extends Pick<NoteSummary, 'content'> {
  content: string;
}

export const useCreateNoteSummary = ({
  noteId,
}: UsedCreateNoteSummaryOptions) =>
  useApiMutation<
    CreateNoteSummaryResponse,
    CreateNoteSummaryError,
    CreateNoteSummaryPayload
  >(`/notes/${noteId}/summaries/`, {
    method: 'POST',
    onSuccess: () => {
      refreshNuxtData(`note:${noteId}:summaries`);
    },
  });
