<template>
  <div>
    <NuxtPage />
    <GuideNotifyDialog />
  </div>
</template>

<script lang="ts" setup>
definePageMeta({
  name: 'home',
  middleware: ['auth'],
  redirect: '/notes',
});
</script>
