import { useQuery } from '@tanstack/vue-query';

type GetNotesResponse = Note[];

interface UseGetNotesOptions {
  type?: NoteType;
  user?: string;
  retrieveMentions?: boolean;
  isCurrentCycle?: Ref<boolean>;
}

export const useGetNotes = ({
  type,
  user,
  retrieveMentions,
  isCurrentCycle,
}: UseGetNotesOptions = {}) => {
  const { $api } = useNuxtApp();

  return useQuery<GetNotesResponse>({
    queryKey: computed(() => [
      'notes',
      type,
      user,
      retrieveMentions,
      isCurrentCycle?.value,
    ]),
    queryFn: () =>
      $api.fetch('/notes/', {
        query: {
          type,
          user,
          retrieve_mentions: retrieveMentions,
          cycle: isCurrentCycle?.value,
        },
      }),
  });
};
