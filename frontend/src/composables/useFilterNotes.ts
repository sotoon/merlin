import { useRouteQuery } from '@vueuse/router';

export const useFilterNotes = (notes: Ref<Note[]> | (() => Note[])) => {
  const writerFilter = useRouteQuery<string>('writer', undefined);
  const yearFilter = useRouteQuery('year', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });
  const periodFilter = useRouteQuery('period', undefined, {
    transform: (value) => (value ? Number(value) : undefined),
  });

  const filteredNotes = computed(() =>
    toValue(notes).filter(
      (note) =>
        note.owner === (writerFilter.value ?? note.owner) &&
        note.year === (yearFilter.value ?? note.year) &&
        note.period === (periodFilter.value ?? note.period),
    ),
  );

  return filteredNotes;
};
