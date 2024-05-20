interface UseStoreDraftOptions<T> {
  disabled?: MaybeRefOrGetter<boolean> | ComputedRef<boolean>;
  setValues: (values: T) => void;
  storageKey: string | MaybeRefOrGetter<string> | ComputedRef<string>;
  values: T | ComputedRef<T>;
}

export const useStoreDraft = <T>({
  disabled,
  values,
  setValues,
  storageKey,
}: UseStoreDraftOptions<T>) => {
  onMounted(() => {
    if (toValue(disabled)) {
      return;
    }

    try {
      const draft = localStorage.getItem(toValue(storageKey));

      if (draft) {
        setValues(JSON.parse(draft));
      }
    } catch (e) {
      localStorage.removeItem(toValue(storageKey));
    }
  });

  watch(
    () => values,
    // TODO: debounce this
    (values) => {
      if (toValue(disabled)) {
        return;
      }

      localStorage.setItem(
        toValue(storageKey),
        JSON.stringify(toValue(values)),
      );
    },
    { deep: true },
  );
};
