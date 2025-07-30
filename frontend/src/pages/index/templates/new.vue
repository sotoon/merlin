<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i
        class="text-h1 text-primary"
        :class="NOTE_TYPE_ICON[NOTE_TYPE.template]"
      />

      <PHeading level="h1" responsive>
        {{ t('note.newTemplate') }}
      </PHeading>
    </div>

    <NoteTemplateForm
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'template-create' });

const { t } = useI18n();
const { mutate: createNote, isPending } = useCreateNote();

const handleSubmit = (
  values: NoteTemplateFormValues,
  ctx: SubmissionContext<NoteTemplateFormValues>,
) => {
  const date = new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote(
    {
      ...values,
      date: dateString,
      type: NOTE_TYPE.template,
    },
    {
      onSuccess: () => {
        ctx.resetForm();
        navigateTo({ name: 'templates' });
      },
    },
  );
};

const handleCancel = () => {
  navigateTo({ name: 'templates' });
};
</script>
