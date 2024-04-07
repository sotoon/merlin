<template>
  <PBox class="bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <NoteForm
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox } from '@pey/core';

definePageMeta({ name: 'note-create' });
const props = defineProps<{ noteType: NoteType }>();

const router = useRouter();
const { execute: createNote, pending } = useCreateNote();

const handleSubmit = (values: NoteFormValues) => {
  const date = new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote({
    body: { ...values, date: dateString, type: props.noteType },
    onSuccess: () => {
      router.back();
    },
  });
};

const handleCancel = () => {
  router.back();
};
</script>
