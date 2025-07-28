<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="text-h1 text-primary" :class="NOTE_TYPE_ICON[note.type]" />

      <PHeading level="h1" responsive>
        {{ t('note.editX', [noteTypeLabels[note.type]]) }}
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

definePageMeta({ name: 'note-edit' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { execute: updateNote, pending } = useUpdateNote(props.note.uuid);

const noteTypeLabels = computed(() => getNoteTypeLabels(t));

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
