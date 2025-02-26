interface FormResultsResponse {
  my_results: FormResults[];
  team_results: FormResults[];
}

export const useGetFormResults = (
  {
    formId,
    cycleId,
  }: {
    formId: string | number;
    cycleId: number;
  },
  {
    enabled,
  }: {
    enabled?: boolean;
  } = {},
) =>
  useApiFetch<FormResultsResponse>(`/forms/${formId}/results/`, {
    key: createNuxtDataKey(['form', formId, 'results', cycleId]),
    query: { cycle_id: cycleId },
    immediate: enabled,
  });
