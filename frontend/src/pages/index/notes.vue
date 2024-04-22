<template>
  <NuxtPage />
</template>

<script lang="ts" setup>
definePageMeta({
  redirect: {
    name: 'notes',
    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.goal] },
  },
});
</script>
