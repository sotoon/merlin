<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="text-h1 text-primary" :class="pageIcon" />

      <PHeading level="h1" responsive>
        {{ pageTitle }}
      </PHeading>
    </div>

    <PChip
      v-if="!isRequestType"
      :icon="PeyInfoIcon"
      :label="t('feedback.feedbackFormHint')"
      variant="ghost"
      color="secondary"
    />

    <NoteForm
      :note-type="NOTE_TYPE.message"
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PChip, PHeading } from '@pey/core';
import { PeyInfoIcon } from '@pey/icons';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'feedback-create' });

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const { execute: createNote, pending } = useCreateNote();

const isRequestType = computed(
  () => route.params.type === FEEDBACK_TYPE.Request,
);
const pageTitle = computed(() =>
  isRequestType.value ? t('common.requestFeedback') : t('common.sendFeedback'),
);
const pageIcon = computed(() =>
  isRequestType.value ? 'i-mdi-comment-question' : 'i-mdi-feedback',
);

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  const title = `${isRequestType.value ? FEEDBACK_REQUEST_PREFIX : ''}${values.title}`;
  const date = values.date || new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote({
    body: { ...values, title, date: dateString, type: NOTE_TYPE.message },
    onSuccess: (newNote) => {
      navigateTo({ name: 'feedback', params: { id: newNote.uuid } });
      ctx.resetForm();
    },
  });
};

const handleCancel = () => {
  router.back();
};
</script>
