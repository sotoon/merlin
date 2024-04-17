<template>
  <NuxtPage />
</template>

<script lang="ts" setup>
definePageMeta({
  redirect: { name: 'notes', params: { type: 'goal' } },
});
</script>
