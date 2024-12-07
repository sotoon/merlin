interface UsedCreateNoteSummaryOptions {
  noteId: string;
}

interface CreateNoteSummaryResponse extends NoteFeedback {}

interface CreateNoteSummaryError {
  detail?: string;
}

interface CreateNoteSummaryPayload
  extends Pick<
    NoteSummary,
    | 'content'
    | 'performance_label'
    | 'ladder_change'
    | 'bonus'
    | 'salary_change'
    | 'committee_date'
  > {
  submit_status?: NoteSummarySubmitStatus;
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
      invalidateNuxtData(['note-summaries', noteId]);
    },
  });
