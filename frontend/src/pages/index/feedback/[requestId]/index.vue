<script lang="ts" setup>
const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
  entries: Schema<'Feedback'>[];
}>();

definePageMeta({ name: 'feedback-detail' });

watch(
  () => props.request.note,
  (newVal) => {
    if (newVal && !newVal.read_status) {
      const { execute } = useUpdateNoteReadStatus({ id: newVal.uuid });
      execute(true);
    }
  },
  { immediate: true },
);
</script>

<template>
  <FeedbackDetail :request="request" :entries="entries" />
</template>
