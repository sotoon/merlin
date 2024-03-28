<template>
  <NuxtPage v-if="noteType" :note-type="noteType" />
</template>

<script lang="ts" setup>
const {
  params: { type },
} = useRoute();

const noteType = computed(() => {
  if (typeof type === 'string' && type in NOTE_TYPE && type !== 'template') {
    return NOTE_TYPE[type as NoteTypeRouteParam];
  }

  return null;
});

onMounted(() => {
  if (!noteType.value) {
    navigateTo({ name: 'notes', replace: true });
  }
});
</script>
