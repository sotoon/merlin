import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';
import type { Note, ProposalType } from '~/types/note';

interface Error {
  detail?: string;
}

export const useGetNote = (id: string) => {
  const { $api } = useNuxtApp();

  return useQuery<Note>({
    queryKey: ['note', id],
    queryFn: () => $api.fetch(`/notes/${id}/`),
  });
};

interface UseGetNotesOptions {
  type?: NoteType;
  user?: string;
  retrieveMentions?: boolean;
  proposalType?: ProposalType;
}

export const useGetNotes = (options: MaybeRef<UseGetNotesOptions> = {}) => {
  const { $api } = useNuxtApp();

  return useQuery<Note[]>({
    queryKey: computed(() => {
      const opts = unref(options);
      return [
        'note-list',
        opts.type,
        opts.user,
        opts.retrieveMentions,
        opts.proposalType,
      ];
    }),
    queryFn: () => {
      const opts = unref(options);
      const params: Record<string, string | undefined> = {
        type: opts.type,
        user: opts.user,
        retrieve_mentions: opts.retrieveMentions ? 'true' : undefined,
        proposal_type: opts.proposalType,
      };

      return $api.fetch('/notes/', { params });
    },
  });
};

export const useCreateNote = () => {
  const { $api } = useNuxtApp();
  const invalidateQueries = useInvalidateQueries();

  return useMutation<Note, Error, Schema<'NoteRequest'>>({
    mutationFn: (data) => $api.fetch('/notes/', { method: 'POST', body: data }),
    onSuccess: () => {
      invalidateQueries('note-list');
    },
  });
};

export const useUpdateNote = (id: string) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();
  const invalidateQueries = useInvalidateQueries();

  return useMutation<Note, Error, Schema<'PatchedNoteRequest'>>({
    mutationFn: (data) =>
      $api.fetch(`/notes/${id}/`, {
        method: 'PATCH',
        body: data,
      }),
    onSuccess: () => {
      invalidateQueries('note-list');
      queryClient.invalidateQueries({ queryKey: ['note', id] });
    },
  });
};

export const useDeleteNote = (id: string) => {
  const { $api } = useNuxtApp();
  const invalidateQueries = useInvalidateQueries();

  return useMutation<never, Error, undefined>({
    mutationFn: () =>
      $api.fetch(`/notes/${id}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      invalidateQueries('note-list');
    },
  });
};

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
