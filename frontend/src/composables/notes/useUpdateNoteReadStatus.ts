interface UpdateNoteReadStatusResponse extends Note {}

interface UseUpdateNoteReadStatusOptions {
  id: string;
}

export const useUpdateNoteReadStatus = ({
  id,
}: UseUpdateNoteReadStatusOptions) => {
  const { data: messages } = useNuxtData<Note[]>(
    createNuxtDataKey(['notes', undefined, undefined, true]),
  );

  const updateMessageNuxtData = (readStatus: boolean) => {
    if (!messages.value) {
      return;
    }

    const messageIndex = messages.value.findIndex(
      (message) => message.uuid === id,
    );

    if (messageIndex < 0) {
      return;
    }

    messages.value[messageIndex].read_status = readStatus;
  };

  const { execute: markAsRead, pending: readPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/read/`, {
    method: 'POST',
    onSuccess: () => {
      updateMessageNuxtData(true);
    },
  });

  const { execute: markAsUnread, pending: unreadPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/unread/`, {
    method: 'POST',
    onSuccess: () => {
      updateMessageNuxtData(false);
    },
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
