<template>
  <NuxtPage />
</template>

<script lang="ts" setup>
definePageMeta({
  name: 'home',
  middleware: ['auth'],
  redirect: '/notes',
});
</script>
