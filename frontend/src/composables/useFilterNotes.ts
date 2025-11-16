import { useRouteQuery } from '@vueuse/router';

const NOTE_SEARCHABLE_KEYS = [
  'content',
  'owner',
  'owner_name',
  'title',
] satisfies (keyof Note)[];

export const useFilterNotes = (notes: Ref<Note[]> | (() => Note[])) => {
  const { data: myTeam } = useGetMyTeam();

  const queryFilter = useRouteQuery<string>('q');
  const typeFilter = useRouteQuery<string>('type');
  const writerFilter = useRouteQuery<string>('writer');
  const yearFilter = useRouteQuery('year', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });
  const periodFilter = useRouteQuery('period', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });
  const teamFilter = useRouteQuery('my-team');
  const unreadFilter = useRouteQuery('unread');
  const proposalTypeFilter = useRouteQuery<string>('proposal_type');

  const filteredNotes = computed(() =>
    toValue(notes).filter(
      (note) =>
        (!queryFilter.value ||
          NOTE_SEARCHABLE_KEYS.some((key) =>
            note[key]?.toLowerCase()?.includes(queryFilter.value.toLowerCase()),
          )) &&
        ((typeFilter.value === NOTE_TYPE.feedback &&
          (note.type === NOTE_TYPE.feedback ||
            note.type === NOTE_TYPE.feedbackRequest)) ||
          note.type === (typeFilter.value ?? note.type)) &&
        note.owner === (writerFilter.value ?? note.owner) &&
        note.year === (yearFilter.value ?? note.year) &&
        note.period === (periodFilter.value ?? note.period) &&
        (!teamFilter.value ||
          myTeam.value?.find((user) => user.email === note.owner)) &&
        (!unreadFilter.value || !note.read_status) &&
        (!proposalTypeFilter.value ||
          note.proposal_type === proposalTypeFilter.value),
    ),
  );

  return filteredNotes;
};
