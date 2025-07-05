import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';

export const useGetFeedbackForms = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-forms'],
    queryFn: () => $api.fetch<Schema<'FeedbackForm'>[]>('/feedback-forms/'),
  });
};

export const useGetFeedbackRequests = (type?: 'owned' | 'invited' | 'all') => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['feedback-requests', type],
    queryFn: () =>
      $api.fetch<Schema<'FeedbackRequestReadOnly'>[]>('/feedback-requests/', {
        params: type && type !== 'all' ? { type } : undefined,
      }),
  });
};

export const useGetAdhocFeedbackEntries = () => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['adhoc-feedback-entries'],
    queryFn: () =>
      $api.fetch<Schema<'Feedback'>[]>('/feedback-entries/', {
        params: { adhoc: 'true' },
      }),
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
      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
      });
    },
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
      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
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
      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
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
      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
      });
      queryClient.invalidateQueries({
        queryKey: ['feedback-request-entries', requestId],
      });
    },
  });
};

export const useGetAdhocFeedbackEntry = (id: string) => {
  const { $api } = useNuxtApp();
  return useQuery({
    queryKey: ['adhoc-feedback-entry', id],
    queryFn: () => $api.fetch<Schema<'Feedback'>>(`/feedback-entries/${id}/`),
  });
};

export const useCreateAdhocFeedbackEntry = () => {
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
      queryClient.invalidateQueries({ queryKey: ['adhoc-feedback-entries'] });
      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
      });
    },
  });
};
