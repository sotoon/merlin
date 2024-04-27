<template>
  <NoteForm
    :note="note"
    :note-type="note.type"
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
  const dateString =
    values.date &&
    `${values.date.getFullYear()}-${values.date.getMonth() + 1}-${values.date.getDate()}`;

  updateNote({
    body: { ...values, date: dateString },
    onSuccess: () => {
      navigateTo({ name: 'note' });
      ctx.resetForm();
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};
</script>
