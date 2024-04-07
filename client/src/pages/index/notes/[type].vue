<template>
  <NuxtPage
    v-if="noteType || (type === 'user' && user)"
    :note-type="noteType"
    :is-user="type === 'user'"
    :user="user"
  />
</template>

<script lang="ts" setup>
const {
  params: { type },
  query,
} = useRoute();
const { data: users } = useGetMyTeam({
  dedupe: 'defer',
  immediate: type === 'user',
});

const noteType = computed(() => {
  if (typeof type === 'string' && type in NOTE_TYPE && type !== 'template') {
    return NOTE_TYPE[type as NoteTypeRouteParam];
  }

  return null;
});

const user = computed(() =>
  users.value?.find(({ email }) => email === query.email),
);

watch([users, user], () => {
  if (type === 'user' && users.value && !user.value) {
    navigateTo({ name: 'my-team', replace: true });
  }
});

onMounted(() => {
  if (!noteType.value && type !== 'user') {
    navigateTo({ name: 'notes', replace: true });
  }
});
</script>
