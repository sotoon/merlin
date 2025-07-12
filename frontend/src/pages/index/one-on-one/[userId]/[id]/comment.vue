<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'one-on-one-comment' });
const props = defineProps<{ oneOnOne: Schema<'OneOnOne'> }>();

const { t } = useI18n();
const {
  query: { owner },
} = useRoute();

const isEditMode = computed(() => Boolean(owner && typeof owner === 'string'));

const { data: userComments, pending: getCommentsPending } = useGetNoteComments({
  noteId: props.oneOnOne.note.uuid,
  owner: isEditMode.value ? (owner as string) : '',
  enabled: isEditMode.value,
});
const { execute: createNoteComment, pending: isSubmitting } =
  useCreateNoteComment(props.oneOnOne.note.uuid);

const handleSubmit = (
  values: Schema<'CommentRequest'>,
  ctx: SubmissionContext<Schema<'CommentRequest'>>,
) => {
  createNoteComment({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      navigateTo({
        name: 'one-on-one-id',
        params: {
          id: props.oneOnOne.note.one_on_one_id,
          userId: props.oneOnOne.note.one_on_one_member,
        },
      });
    },
  });
};

const handleCancel = () => {
  navigateTo({
    name: 'one-on-one-id',
    params: {
      id: props.oneOnOne.note.one_on_one_id,
      userId: props.oneOnOne.note.one_on_one_member,
    },
  });
};
</script>

<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.writeCommentFor', { title: oneOnOne.note.title }) }}
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
