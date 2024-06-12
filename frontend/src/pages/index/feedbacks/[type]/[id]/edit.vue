<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="text-h1 text-primary" :class="pageIcon" />

      <PHeading level="h1" responsive>
        {{ pageTitle }}
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
const route = useRoute();
const { execute: updateNote, pending } = useUpdateNote({ id: props.note.uuid });

const isRequestType = computed(
  () => route.params.type === FEEDBACK_TYPE.Request,
);
const pageTitle = computed(() =>
  isRequestType.value
    ? t('note.editX', [t('common.requestFeedback')])
    : t('note.editX', [t('common.feedback')]),
);
const pageIcon = computed(() =>
  isRequestType.value ? 'i-mdi-comment-question' : 'i-mdi-feedback',
);

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  const title = `${route.params.type === FEEDBACK_TYPE.Request ? FEEDBACK_REQUEST_PREFIX : ''}${values.title}`;
  const dateString =
    values.date &&
    `${values.date.getFullYear()}-${values.date.getMonth() + 1}-${values.date.getDate()}`;

  updateNote({
    body: { ...values, title, date: dateString },
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
