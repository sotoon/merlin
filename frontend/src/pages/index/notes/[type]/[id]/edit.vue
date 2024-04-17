<template>
  <NoteForm
    :note="note"
    :is-submitting="pending"
    @submit="handleSubmit"
    @cancel="handleCancel"
  />
</template>

<script lang="ts" setup>
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-edit' });
const props = defineProps<{ note: Note }>();

const { execute: updateNote, pending } = useUpdateNote({ id: props.note.uuid });

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  updateNote({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      navigateTo({ name: 'note' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};
</script>
