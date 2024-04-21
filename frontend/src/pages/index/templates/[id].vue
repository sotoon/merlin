<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.editTemplate') }}
    </PHeading>

    <PLoading v-if="pending" class="text-primary" :size="20" />

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{
          error.statusCode === 404
            ? t('note.noteNotFound')
            : t('note.getNoteError')
        }}
      </PText>

      <PButton
        v-if="error.statusCode !== 404"
        color="gray"
        :icon-start="PeyRetryIcon"
        @click="refresh"
      >
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NoteTemplateForm
      v-else-if="note"
      :note="note"
      :is-submitting="isSubmitting"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PButton, PHeading, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'template' });

const { t } = useI18n();
const {
  params: { id },
} = useRoute();

const noteId = computed(() => {
  if (typeof id === 'string') {
    return id;
  }

  return '';
});

const {
  data: note,
  pending,
  error,
  refresh,
} = useGetNote({ id: noteId.value });
const { execute: updateNote, pending: isSubmitting } = useUpdateNote({
  id: noteId.value,
});

const handleSubmit = (
  values: NoteTemplateFormValues,
  ctx: SubmissionContext<NoteTemplateFormValues>,
) => {
  updateNote({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      navigateTo({ name: 'templates' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'templates' });
};
</script>
