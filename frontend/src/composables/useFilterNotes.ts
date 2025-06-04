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
  const teamFilter = useRouteQuery('my-team');
  const unreadFilter = useRouteQuery('unread');

  const filteredNotes = computed(() =>
    toValue(notes).filter(
      (note) =>
        (!queryFilter.value ||
          NOTE_SEARCHABLE_KEYS.some((key) =>
            note[key]?.toLowerCase()?.includes(queryFilter.value.toLowerCase()),
          )) &&
        note.type === (typeFilter.value ?? note.type) &&
        note.owner === (writerFilter.value ?? note.owner) &&
        (!teamFilter.value ||
          myTeam.value?.find((user) => user.email === note.owner)) &&
        (!unreadFilter.value || !note.read_status),
    ),
  );

  return filteredNotes;
};
