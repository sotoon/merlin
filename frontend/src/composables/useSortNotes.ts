const SORT_FUNCTIONS = {
  [NOTE_SORT_OPTION.update]: (a: Note, b: Note) =>
    new Date(b.date_updated).getTime() - new Date(a.date_updated).getTime(),
  [NOTE_SORT_OPTION.period]: (a: Note, b: Note) =>
    (b.year - a.year) * 10 + (b.period - a.period),
  [NOTE_SORT_OPTION.date]: (a: Note, b: Note) =>
    new Date(b.date).getTime() - new Date(a.date).getTime(),
};

export const useSortNotes = (notes: Note[]) => {
  const route = useRoute();

  const sortModel = computed({
    get() {
      if (!route.query.sort) {
        return NOTE_SORT_OPTION.update;
      }

      if (
        typeof route.query.sort !== 'string' ||
        !(route.query.sort in NOTE_SORT_OPTION)
      ) {
        sortModel.value = NOTE_SORT_OPTION.update;

        return NOTE_SORT_OPTION.update;
      }

      return route.query
        .sort as (typeof NOTE_SORT_OPTION)[keyof typeof NOTE_SORT_OPTION];
    },
    set(value) {
      navigateTo({
        query: { ...route.query, sort: value },
        replace: true,
      });
    },
  });

  const sortedNotes = computed(() =>
    [...notes].sort(SORT_FUNCTIONS[sortModel.value]),
  );

  return { sortModel, sortedNotes };
};
