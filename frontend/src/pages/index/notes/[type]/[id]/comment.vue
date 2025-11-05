<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{
        t(
          note.type === NOTE_TYPE.proposal
            ? 'note.writeFeedbackFor'
            : 'note.writeCommentFor',
          { title: note.title },
        )
      }}
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

<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-comment' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const {
  query: { owner },
} = useRoute();

const isEditMode = computed(() => Boolean(owner && typeof owner === 'string'));

const { data: userComments, isPending: getCommentsPending } =
  useGetNoteComments({
    noteId: props.note.uuid,
    owner: isEditMode.value ? (owner as string) : '',
    enabled: isEditMode.value,
  });
const { mutate: createNoteComment, isPending: isSubmitting } =
  useCreateNoteComment(props.note.uuid);

const handleSubmit = (
  values: Schema<'CommentRequest'>,
  ctx: SubmissionContext<Schema<'CommentRequest'>>,
) => {
  createNoteComment(
    { ...values },
    {
      onSuccess: () => {
        ctx.resetForm();
        navigateTo({ name: 'note' });
      },
    },
  );
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};
</script>
