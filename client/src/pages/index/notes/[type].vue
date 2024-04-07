<template>
  <NuxtPage
    :note-type="noteType || undefined"
    :user-email="typeof query.user === 'string' ? query.user : undefined"
    :user="user"
  />
</template>

<script lang="ts" setup>
const { params, query } = useRoute();
const { data: users } = useGetMyTeam({
  dedupe: 'defer',
  immediate: Boolean(query.user),
});

const noteType = computed(() => {
  if (
    typeof params.type === 'string' &&
    params.type in NOTE_TYPE &&
    params.type !== 'template'
  ) {
    return NOTE_TYPE[params.type as NoteTypeRouteParam];
  }

  return null;
});

const user = computed(() =>
  users.value?.find(({ email }) => email === query.user),
);

const isValidRoute = computed(() => {
  if (params.type === '-' && (query.user || params.id)) {
    return true;
  }

  if (params.type !== '-' && noteType.value) {
    return true;
  }

  return false;
});

watch([users, user], () => {
  if (query.user && users.value && !user.value) {
    navigateTo({ name: 'my-team', replace: true });
  }
});

onMounted(() => {
  if (isValidRoute.value) {
    return;
  }

  navigateTo({ name: 'home', replace: true });
});
</script>
