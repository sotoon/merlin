<script lang="ts" setup>
defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
  entries: Schema<'Feedback'>[];
}>();

definePageMeta({ name: 'feedback-detail' });
</script>

<template>
  <FeedbackDetail :request="request" :entries="entries" />
</template>
