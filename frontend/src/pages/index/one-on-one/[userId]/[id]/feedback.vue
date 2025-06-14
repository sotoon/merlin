<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'one-on-one-feedback' });
const props = defineProps<{ oneOnOne: Schema<'OneOnOne'> }>();

const { t } = useI18n();
const {
  query: { owner },
} = useRoute();

const isEditMode = computed(() => Boolean(owner && typeof owner === 'string'));

const { data: userFeedbacks, pending: getFeedbacksPending } =
  useGetNoteFeedbacks({
    noteId: props.oneOnOne.note.uuid,
    owner: isEditMode.value ? (owner as string) : '',
    enabled: isEditMode.value,
  });
const { execute: createNoteFeedback, pending: isSubmitting } =
  useCreateNoteFeedback({ noteId: props.oneOnOne.note.uuid });

const handleSubmit = (
  values: NoteFeedbackFormValues,
  ctx: SubmissionContext<NoteFeedbackFormValues>,
) => {
  createNoteFeedback({
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
      {{ t('note.writeFeedbackFor', { title: oneOnOne.note.title }) }}
    </PHeading>

    <PLoading
      v-if="isEditMode && getFeedbacksPending"
      class="text-primary"
      :size="20"
    />

    <NoteFeedbackForm
      v-else
      :feedback="isEditMode ? userFeedbacks?.[0] : undefined"
      :is-submitting="isSubmitting"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>
