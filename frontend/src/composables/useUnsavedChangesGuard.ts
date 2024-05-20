interface UseUnsavedChangesGuardOptions {
  disabled?: boolean | MaybeRefOrGetter<boolean> | ComputedRef<boolean>;
}

export const useUnsavedChangesGuard = ({
  disabled,
}: UseUnsavedChangesGuardOptions = {}) => {
  const handleBeforeUnload = (event: BeforeUnloadEvent) => {
    if (!toValue(disabled)) {
      event.preventDefault();
    }
  };

  onMounted(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
  });

  onUnmounted(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
  });

  onBeforeRouteLeave((to, from, next) => {
    if (toValue(disabled)) {
      next();

      return;
    }

    const answer = window.confirm(
      'Do you really want to leave? you have unsaved changes!',
    );

    if (answer) {
      next();
    } else {
      next(false);
    }
  });
};
