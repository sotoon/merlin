interface UpdateNoteReadStatusResponse extends Note {}

interface UseUpdateNoteReadStatusOptions {
  id: string;
}

export const useUpdateNoteReadStatus = ({
  id,
}: UseUpdateNoteReadStatusOptions) => {
  const nuxtApp = useNuxtApp();

  const updateNoteReadStatus = (readStatus: boolean) => {
    const nuxtData = nuxtApp.payload.data;

    const notesDataKeys = Object.keys(nuxtData).filter((key) =>
      key.match(/^notes::.*:(true)?$/),
    );

    notesDataKeys.forEach((key) => {
      const messageIndex = nuxtData[key].findIndex(
        (message: Note) => message.uuid === id,
      );

      if (messageIndex < 0) {
        return;
      }

      nuxtData[key][messageIndex].read_status = readStatus;
    });
  };

  const { execute: markAsRead, pending: readPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/read/`, {
    method: 'POST',
    onSuccess: () => {
      updateNoteReadStatus(true);
    },
  });

  const { execute: markAsUnread, pending: unreadPending } = useApiMutation<
    UpdateNoteReadStatusResponse,
    unknown,
    never
  >(`/notes/${id}/unread/`, {
    method: 'POST',
    onSuccess: () => {
      updateNoteReadStatus(false);
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
