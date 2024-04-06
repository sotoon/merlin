<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.writeFeedbackFor', { title: note.title }) }}
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

<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';

definePageMeta({ name: 'note-feedback' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const {
  query: { owner },
} = useRoute();

const isEditMode = computed(() => Boolean(owner && typeof owner === 'string'));

const { data: userFeedbacks, pending: getFeedbacksPending } =
  useGetNoteFeedbacks({
    noteId: props.note.uuid,
    owner: isEditMode.value ? (owner as string) : '',
    enabled: isEditMode.value,
  });
const { execute: updateNote, pending: isSubmitting } = useCreateNoteFeedback({
  noteId: props.note.uuid,
  owner: isEditMode.value ? (owner as string) : undefined,
});

const handleSubmit = (values: NoteFeedbackFormValues) => {
  updateNote({
    body: values,
    onSuccess: () => {
      navigateTo({ name: 'note' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};
</script>
