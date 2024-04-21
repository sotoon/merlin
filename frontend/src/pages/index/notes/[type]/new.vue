<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <NoteForm
      :note-type="noteType"
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-create' });
const props = defineProps<{ noteType: NoteType }>();

const router = useRouter();
const { execute: createNote, pending } = useCreateNote();

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  const date = values.date || new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote({
    body: { ...values, date: dateString, type: props.noteType },
    onSuccess: () => {
      ctx.resetForm();
      router.back();
    },
  });
};

const handleCancel = () => {
  router.back();
};
</script>
