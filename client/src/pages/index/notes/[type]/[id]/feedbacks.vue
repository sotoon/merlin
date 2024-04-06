<template>
  <div>Note Feedback: {{ owner }}</div>
</template>

<script lang="ts" setup>
definePageMeta({ name: 'note-feedback' });

const {
  query: { owner },
} = useRoute();
</script>
