<template>
  <PLoading v-if="pending" class="text-primary" />

  <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
    <PText as="p" class="text-center text-danger" responsive>
      {{
        noteIsFeedback
          ? t('note.getResponsesError')
          : t('note.getFeedbacksError')
      }}
    </PText>

    <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
      {{ t('common.retry') }}
    </PButton>
  </div>

  <template v-else-if="feedbacks?.length">
    <div
      class="flex items-center justify-between gap-4 border-b border-gray-10 pb-4"
    >
      <PHeading :lvl="3" responsive>
        {{ noteIsFeedback ? t('note.responses') : t('note.feedbacks') }}
      </PHeading>

      <PIconButton
        v-if="note.access_level.can_write_feedback"
        class="shrink-0"
        :icon="userFeedbacks?.length ? PeyEditIcon : PeyPlusIcon"
        type="button"
        @click="handleShowForm"
      />
    </div>

    <div class="px-4">
      <NoteFeedbackList :note="note" :feedbacks="feedbacks" />
    </div>
  </template>

  <div v-if="note.access_level.can_write_feedback">
    <div v-if="showForm" ref="formRef" class="p-4">
      <NoteFeedbackForm
        v-model:visible="showForm"
        :note="note"
        :feedback="userFeedbacks?.length ? userFeedbacks?.[0] : undefined"
      />
    </div>

    <PButton
      v-else-if="!userFeedbacks?.length"
      type="button"
      :icon-start="PeyPlusIcon"
      variant="ghost"
      @click="handleShowForm"
    >
      {{ noteIsFeedback ? t('note.writeResponse') : t('note.writeFeedback') }}
    </PButton>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyEditIcon, PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const formRef = ref<HTMLElement | null>(null);
const showForm = ref(false);

const { t } = useI18n();
const {
  data: feedbacks,
  pending,
  error,
  refresh,
} = useGetNoteFeedbacks({
  noteId: props.note.uuid,
});
const { data: profile } = useGetProfile();

const noteIsFeedback = computed(
  () => props.note.feedbackType === FEEDBACK_TYPE.Send,
);
const userFeedbacks = computed(() =>
  feedbacks.value?.filter(
    (feedback) => feedback.owner === profile.value?.email,
  ),
);

const handleShowForm = () => {
  showForm.value = true;
  nextTick(() => {
    formRef.value?.scrollIntoView({ behavior: 'smooth' });
  });
};
</script>
