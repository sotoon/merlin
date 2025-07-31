<script lang="ts" setup>
import { useQueryClient } from '@tanstack/vue-query';

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
  entries: Schema<'Feedback'>[];
}>();

definePageMeta({ name: 'feedback-detail' });
const queryClient = useQueryClient();
const { mutate: updateReadStatus } = useUpdateNoteReadStatus();

watch(
  () => props.request.note,
  (newVal) => {
    if (newVal && !newVal.read_status) {
      updateReadStatus(newVal.uuid, true);

      queryClient.invalidateQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'feedback-requests';
        },
      });
    }
  },
  { immediate: true },
);
watch(
  () => props.entries,
  (newVal) => {
    newVal.forEach(({ note }) => {
      if (note && !note.read_status) {
        updateReadStatus(note.uuid, true);
      }
    });
  },
  { immediate: true },
);
</script>

<template>
  <FeedbackDetail :request="request" :entries="entries" />
</template>
