import { useRouteQuery } from '@vueuse/router';

const SORT_FUNCTIONS = {
  [NOTE_SORT_OPTION.update]: (a: Note, b: Note) =>
    new Date(b.date_updated).getTime() - new Date(a.date_updated).getTime(),
  [NOTE_SORT_OPTION.period]: (a: Note, b: Note) =>
    (b.year - a.year) * 10 + (b.period - a.period),
  [NOTE_SORT_OPTION.date]: (a: Note, b: Note) =>
    new Date(b.date).getTime() - new Date(a.date).getTime(),
};

export const useSortNotes = (notes: Ref<Note[]> | (() => Note[])) => {
  const sortModel = useRouteQuery('sort', NOTE_SORT_OPTION.update);

  const sortedNotes = computed(() =>
    [...toValue(notes)].sort(SORT_FUNCTIONS[sortModel.value]),
  );

  return sortedNotes;
};
