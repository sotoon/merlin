import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';

export const useGetFeedbackForms = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-forms'],
    queryFn: () => $api.fetch<Schema<'FeedbackForm'>[]>('/feedback-forms/'),
  });
};

export const useGetFeedbackRequestsOwned = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-requests-owned'],
    queryFn: () =>
      $api.fetch<Schema<'FeedbackRequestReadOnly'>[]>(
        '/feedback-requests/owned/',
      ),
  });
};

export const useGetFeedbackRequestsInvited = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-requests-invited'],
    queryFn: () =>
      $api.fetch<Schema<'FeedbackRequestReadOnly'>[]>(
        '/feedback-requests/invited/',
      ),
  });
};

export const useCreateFeedbackRequest = () => {
  const queryClient = useQueryClient();
  const { $api } = useNuxtApp();

  return useMutation<
    Schema<'FeedbackRequestReadOnly'>,
    { detail?: string },
    Schema<'FeedbackRequestWriteRequest'>
  >({
    mutationFn: (data) =>
      $api.fetch('/feedback-requests/', {
        method: 'POST',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback-requests'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests-owned'] });
      queryClient.invalidateQueries({
        queryKey: ['feedback-requests-invited'],
      });
    },
  });
};

export const useGetFeedbackRequests = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-requests'],
    queryFn: () =>
      $api.fetch<Schema<'FeedbackRequestReadOnly'>[]>('/feedback-requests/'),
  });
};

export const useGetFeedbackRequest = (id: string) => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-request', id],
    queryFn: () =>
      $api.fetch<Schema<'FeedbackRequestReadOnly'>>(
        `/feedback-requests/${id}/`,
      ),
  });
};

export const useGetFeedbackRequestEntries = (id: string) => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-request-entries', id],
    queryFn: () =>
      $api.fetch<Schema<'Feedback'>[]>(`/feedback-requests/${id}/entries/`),
  });
};

export const useUpdateFeedbackRequest = (id: string) => {
  const queryClient = useQueryClient();
  const { $api } = useNuxtApp();

  return useMutation<
    Schema<'FeedbackRequestWrite'>,
    { detail?: string },
    Schema<'PatchedFeedbackRequestWriteRequest'>
  >({
    mutationFn: (data) =>
      $api.fetch(`/feedback-requests/${id}/`, {
        method: 'PATCH',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback-request', id] });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests-owned'] });
      queryClient.invalidateQueries({
        queryKey: ['feedback-requests-invited'],
      });
    },
  });
};

export const useDeleteFeedbackRequest = (id: string) => {
  const queryClient = useQueryClient();
  const { $api } = useNuxtApp();

  return useMutation<void, { detail?: string }, null>({
    mutationFn: () =>
      $api.fetch(`/feedback-requests/${id}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedback-request'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests-owned'] });
      queryClient.invalidateQueries({
        queryKey: ['feedback-requests-invited'],
      });
    },
  });
};

export const useCreateFeedbackEntry = (requestId: string) => {
  const queryClient = useQueryClient();
  const { $api } = useNuxtApp();

  return useMutation<
    Schema<'Feedback'>,
    { detail?: string },
    Schema<'FeedbackRequest'>
  >({
    mutationFn: (data) =>
      $api.fetch('/feedback-entries/', {
        method: 'POST',
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['feedback-request', requestId],
      });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests'] });
      queryClient.invalidateQueries({ queryKey: ['feedback-requests-owned'] });
      queryClient.invalidateQueries({
        queryKey: ['feedback-requests-invited'],
      });
      queryClient.invalidateQueries({
        queryKey: ['feedback-request-entries', requestId],
      });
    },
  });
};
