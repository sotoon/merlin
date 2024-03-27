<template>
  <NoteForm
    :note="note"
    :is-submitting="pending"
    @submit="handleSubmit"
    @cancel="handleCancel"
  />
</template>

<script lang="ts" setup>
definePageMeta({ name: 'note-edit' });
const props = defineProps<{ note: Note }>();

const { execute: updateNote, pending } = useUpdateNote({ id: props.note.uuid });

const handleSubmit = (values: NoteFormValues) => {
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
</script>
