import { useQueryClient, useMutation } from '@tanstack/vue-query';

export const useUpdateNoteReadStatus = () => {
  const queryClient = useQueryClient();
  const { $api } = useNuxtApp();

  const { mutate: markAsRead, isPending: readPending } = useMutation({
    mutationFn: (id: string) =>
      $api.fetch(`/notes/${id}/read/`, { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          return (
            query.queryKey[0] === 'note' || query.queryKey[0] === 'note-list'
          );
        },
      });
    },
  });

  const { mutate: markAsUnread, isPending: unreadPending } = useMutation({
    mutationFn: (id: string) =>
      $api.fetch(`/notes/${id}/unread/`, { method: 'POST' }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        predicate: (query) => {
          return (
            query.queryKey[0] === 'note' || query.queryKey[0] === 'note-list'
          );
        },
      });
    },
  });

  const mutate = (id: string, readStatus: boolean) => {
    if (readStatus) {
      markAsRead(id);
    } else {
      markAsUnread(id);
    }
  };

  const isPending = computed(() => readPending.value || unreadPending.value);

  return { mutate, isPending };
};
