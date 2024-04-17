<template>
  <NuxtPage
    :note-type="noteType || undefined"
    :user-email="
      typeof route.query.user === 'string' ? route.query.user : undefined
    "
    :user="user"
  />
</template>

<script lang="ts" setup>
const route = useRoute();
const { data: users, refresh: getMyTeam } = useGetMyTeam({
  immediate: Boolean(route.query.user),
});

const noteType = computed(() => {
  if (
    typeof route.params.type === 'string' &&
    route.params.type in NOTE_TYPE &&
    route.params.type !== 'template'
  ) {
    return NOTE_TYPE[route.params.type as NoteTypeRouteParam];
  }

  return null;
});

const user = computed(() =>
  users.value?.find(({ email }) => email === route.query.user),
);

const isValidRoute = computed(() => {
  if (route.params.type === '-' && (route.query.user || route.params.id)) {
    return true;
  }

  if (route.params.type !== '-' && noteType.value) {
    return true;
  }

  return false;
});

watch([users, user], () => {
  if (route.query.user && users.value && !user.value) {
    navigateTo({ name: 'my-team', replace: true });
  }
});

watch(
  () => route.query.user,
  () => {
    getMyTeam();
  },
);

onMounted(() => {
  if (isValidRoute.value) {
    return;
  }

  navigateTo({ name: 'home', replace: true });
});
</script>
