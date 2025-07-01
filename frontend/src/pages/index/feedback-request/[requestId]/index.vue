<script lang="ts" setup>
defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
  entries: Schema<'Feedback'>[];
}>();

definePageMeta({ name: 'feedback-request-detail' });
</script>

<template>
  <FeedbackRequestDetail :request="request" :entries="entries" />
</template>
