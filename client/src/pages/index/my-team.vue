<template>
  <NuxtPage />
</template>

<script lang="ts" setup>
const { data: users } = useGetMyTeam({ dedupe: 'defer' });

watch(users, () => {
  if (users.value && !users.value.length) {
    navigateTo({ name: 'home', replace: true });
  }
});
</script>
