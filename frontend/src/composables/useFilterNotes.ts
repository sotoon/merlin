import { useRouteQuery } from '@vueuse/router';

export const useFilterNotes = (notes: Ref<Note[]> | (() => Note[])) => {
  const typeFilter = useRouteQuery<string>('type');
  const writerFilter = useRouteQuery<string>('writer');
  const yearFilter = useRouteQuery('year', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });
  const periodFilter = useRouteQuery('period', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });
  const unreadFilter = useRouteQuery('unread');

  const filteredNotes = computed(() =>
    toValue(notes).filter(
      (note) =>
        note.type === (typeFilter.value ?? note.type) &&
        note.owner === (writerFilter.value ?? note.owner) &&
        note.year === (yearFilter.value ?? note.year) &&
        note.period === (periodFilter.value ?? note.period) &&
        (!unreadFilter.value || !note.read_status),
    ),
  );

  return filteredNotes;
};
