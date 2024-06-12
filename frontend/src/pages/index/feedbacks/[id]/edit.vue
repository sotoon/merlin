<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-feedback text-h1 text-primary" />

      <PHeading level="h1" responsive>
        {{ t('note.editX', [t('common.feedback')]) }}
      </PHeading>
    </div>

    <NoteForm
      :note="note"
      :note-type="note.type"
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>

<script lang="ts" setup>
import { PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'feedback-edit' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
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
      navigateTo({ name: 'feedback' });
      ctx.resetForm();
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};
</script>
