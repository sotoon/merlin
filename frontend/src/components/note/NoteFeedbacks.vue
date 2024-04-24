<template>
  <PLoading v-if="pending" class="text-primary" />

  <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
    <PText as="p" class="text-center text-danger" responsive>
      {{ t('note.getFeedbacksError') }}
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
        {{ t('note.feedbacks') }}
      </PHeading>

      <PIconButton
        v-if="note.access_level.can_write_feedback"
        class="shrink-0"
        :icon="userHasWrittenFeedback ? PeyEditIcon : PeyPlusIcon"
        type="button"
        @click="
          navigateTo({
            name: 'note-feedback',
            query: {
              owner: userHasWrittenFeedback ? profile?.email : undefined,
            },
          })
        "
      />
    </div>

    <div class="p-4">
      <NoteFeedbackList :feedbacks="feedbacks" />
    </div>
  </template>

  <PButton
    v-else-if="note.access_level.can_write_feedback"
    :icon-start="PeyPlusIcon"
    variant="ghost"
    @click="navigateTo({ name: 'note-feedback' })"
  >
    {{ t('note.writeFeedback') }}
  </PButton>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyEditIcon, PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

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

const userHasWrittenFeedback = computed(() =>
  feedbacks.value?.some((feedback) => feedback.owner === profile.value?.email),
);
</script>
