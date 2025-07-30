import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';
import type { Note, ProposalType } from '~/types/note';

// Get single note
type GetNoteResponse = Note | null;

interface Error {
  detail?: string;
}

export const useGetNote = (
  id: string,
  fetchOptions: UseApiFetchOptions<GetNoteResponse> = {},
) => {
  const { $api } = useNuxtApp();

  return useQuery<GetNoteResponse>({
    queryKey: ['note', id],
    queryFn: () => $api.fetch<GetNoteResponse>(`/notes/${id}/`),
    ...fetchOptions,
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

interface CreateNotePayload
  extends Pick<
    Partial<Note>,
    | 'title'
    | 'content'
    | 'type'
    | 'mentioned_users'
    | 'year'
    | 'period'
    | 'linked_notes'
    | 'submit_status'
    | 'proposal_type'
  > {
  content: string;
  date: string;
  title: string;
}

export const useCreateNote = () => {
  const { $api } = useNuxtApp();
  const invalidateQueries = useInvalidateQueries();

  return useMutation<Note, Error, CreateNotePayload>({
    mutationFn: (data) => $api.fetch('/notes/', { method: 'POST', body: data }),
    onSuccess: () => {
      invalidateQueries('note-list');
    },
  });
};

interface UpdateNotePayload
  extends Pick<
    Partial<Note>,
    | 'title'
    | 'content'
    | 'mentioned_users'
    | 'date'
    | 'year'
    | 'period'
    | 'linked_notes'
    | 'submit_status'
    | 'proposal_type'
  > {}

export const useUpdateNote = (id: string) => {
  const { $api } = useNuxtApp();
  const queryClient = useQueryClient();
  const invalidateQueries = useInvalidateQueries();

  return useMutation<Note, Error, UpdateNotePayload>({
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
