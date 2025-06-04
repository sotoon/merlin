import { useRouteQuery } from '@vueuse/router';

const SORT_FUNCTIONS: Record<
  (typeof NOTE_SORT_OPTION)[keyof typeof NOTE_SORT_OPTION],
  (a: Note, b: Note) => number
> = {
  [NOTE_SORT_OPTION.update]: (a, b) =>
    new Date(b.date_updated).getTime() - new Date(a.date_updated).getTime(),
  [NOTE_SORT_OPTION.newest]: (a, b) =>
    new Date(b.date_created).getTime() - new Date(a.date_created).getTime(),
  [NOTE_SORT_OPTION.oldest]: (a, b) =>
    new Date(a.date_created).getTime() - new Date(b.date_created).getTime(),
  [NOTE_SORT_OPTION.date]: (a, b) =>
    new Date(b.date).getTime() - new Date(a.date).getTime(),
  [NOTE_SORT_OPTION.title]: (a, b) => a.title.localeCompare(b.title),
};

export const useSortNotes = (notes: Ref<Note[]> | (() => Note[])) => {
  const sortModel = useRouteQuery('sort', NOTE_SORT_OPTION.update);

  const sortedNotes = computed(() =>
    [...toValue(notes)].sort(SORT_FUNCTIONS[sortModel.value]),
  );

  return sortedNotes;
};
