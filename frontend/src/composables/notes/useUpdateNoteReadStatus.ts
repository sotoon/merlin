interface UpdateNoteReadStatusResponse extends Note {}

interface UseUpdateNoteReadStatusOptions {
  id: string;
}

export const useUpdateNoteReadStatus = ({
  id,
}: UseUpdateNoteReadStatusOptions) => {
  const { execute: markAsRead, pending: readPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/read/`, {
    method: 'POST',
  });

  const { execute: markAsUnread, pending: unreadPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/unread/`, {
    method: 'POST',
  });

  const execute = (
    readStatus: boolean,
    options: { onSuccess?: () => void } = {},
  ) => {
    if (readStatus) {
      markAsRead(options);
    } else {
      markAsUnread(options);
    }
  };

  const pending = computed(() => readPending.value || unreadPending.value);

  return { execute, pending };
};
