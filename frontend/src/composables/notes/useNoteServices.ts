import { useQuery } from '@tanstack/vue-query';
import { useQueryClient } from '@tanstack/vue-query';
import type { Note, ProposalType } from '~/types/note';

// Get single note
type GetNoteResponse = Note | null;

export const useGetNote = (
  id: string,
  fetchOptions: UseApiFetchOptions<GetNoteResponse> = {},
) =>
  useApiFetch<GetNoteResponse>(`/notes/${id}/`, {
    key: createNuxtDataKey(['note', id]),
    ...fetchOptions,
  });

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
        'notes',
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
  const queryClient = useQueryClient();

  return useApiMutation<
    Note,
    {
      detail?: string;
    },
    CreateNotePayload
  >('/notes/', {
    method: 'POST',
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['notes'],
      });
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
  const queryClient = useQueryClient();

  return useApiMutation<
    Note,
    {
      detail?: string;
    },
    UpdateNotePayload
  >(`/notes/${id}/`, {
    method: 'PATCH',
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['notes'],
      });
    },
  });
};
