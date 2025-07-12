<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'adhoc-comment' });
const props = defineProps<{ entry: Schema<'Feedback'> }>();

const { t } = useI18n();
const {
  query: { owner },
} = useRoute();

const isEditMode = computed(() => Boolean(owner && typeof owner === 'string'));

const { data: userComments, pending: getCommentsPending } = useGetNoteComments({
  noteId: props.entry.note.uuid,
  owner: isEditMode.value ? (owner as string) : '',
  enabled: isEditMode.value,
});
const { execute: createNoteComment, pending: isSubmitting } =
  useCreateNoteComment(props.entry.note.uuid);

const handleSubmit = (
  values: Schema<'CommentRequest'>,
  ctx: SubmissionContext<Schema<'CommentRequest'>>,
) => {
  createNoteComment({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      navigateTo({
        name: 'adhoc-feedback-detail',
        params: {
          id: props.entry.uuid,
        },
      });
    },
  });
};

const handleCancel = () => {
  navigateTo({
    name: 'adhoc-feedback-detail',
    params: {
      id: props.entry.uuid,
    },
  });
};
</script>

<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.writeCommentFor', { title: entry.note.title }) }}
    </PHeading>

    <PLoading
      v-if="isEditMode && getCommentsPending"
      class="text-primary"
      :size="20"
    />

    <NoteCommentForm
      v-else
      :comment="isEditMode ? userComments?.[0] : undefined"
      :is-submitting="isSubmitting"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>
