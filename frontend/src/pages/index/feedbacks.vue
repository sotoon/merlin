<template>
  <NuxtPage />
</template>

<script lang="ts" setup>
definePageMeta({
  redirect: {
    name: 'feedbacks',
    params: { type: FEEDBACK_TYPE.Send },
  },
});
</script>
