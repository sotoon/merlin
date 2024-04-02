<template>
  <NoteSummaryForm
    :note="note"
    :is-submitting="pending"
    @submit="handleSubmit"
    @cancel="handleCancel"
  />
</template>

<script lang="ts" setup>
definePageMeta({ name: 'note-summary' });
const props = defineProps<{ note: Note }>();

const { execute: updateNote, pending } = useUpdateNote({ id: props.note.uuid });

const handleSubmit = (values: NoteSummaryFormValues) => {
  updateNote({
    body: values,
    onSuccess: () => {
      navigateTo({ name: 'note' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};

onMounted(() => {
  if (!props.note.access_level.can_write_summary) {
    navigateTo({ name: 'note', replace: true });
  }
});
</script>
