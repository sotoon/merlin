<script setup lang="ts">
import { PButton, PLoading, PText, PTabs, PTab } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import { useRouteQuery } from '@vueuse/router';

definePageMeta({ name: 'feedback' });

const { t } = useI18n();

const tabOptions = ['owned', 'invited'] as const;
const tabFilter = useRouteQuery<'owned' | 'invited'>('tab', 'owned');

const currentTabIndex = computed(() => {
  return tabOptions.indexOf(tabFilter.value as any) || 0;
});

const handleTabChange = (index: number) => {
  tabFilter.value = tabOptions[index];
};

const {
  data: ownedRequests,
  isPending: ownedPending,
  isError: ownedError,
  refetch: ownedRefresh,
} = useGetFeedbackRequests('owned');
const {
  data: invitedRequests,
  isPending: invitedPending,
  isError: invitedError,
  refetch: invitedRefresh,
} = useGetFeedbackRequests('invited');

const { data: messages } = useGetNotes({ retrieveMentions: true });
const newFeedbackCount = computed(
  () =>
    (messages.value || []).filter(
      (message) =>
        message.type === NOTE_TYPE.feedbackRequest && !message.read_status,
    ).length,
);
const receivedFeedbackCount = computed(
  () =>
    (messages.value || []).filter(
      (message) =>
        message.type === NOTE_TYPE.feedback &&
        message.feedback_request_uuid &&
        !message.read_status,
    ).length,
);
</script>

<template>
  <div>
    <PTabs :model-value="currentTabIndex" @update:model-value="handleTabChange">
      <PTab :title="t('feedback.ownedRequests')">
        <template #prepend>
          <Badge :count="receivedFeedbackCount" :max="999" />
        </template>

        <div v-if="ownedPending" class="flex items-center justify-center py-8">
          <PLoading class="text-primary" :size="20" />
        </div>
        <div
          v-else-if="ownedError"
          class="flex flex-col items-center gap-4 py-8"
        >
          <PText as="p" class="text-center text-danger" responsive>
            {{ t('feedback.getError') }}
          </PText>
          <PButton
            color="gray"
            :icon-start="PeyRetryIcon"
            @click="ownedRefresh"
          >
            {{ t('common.retry') }}
          </PButton>
        </div>
        <div
          v-else-if="ownedRequests?.length"
          class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
        >
          <FeedbackCard
            v-for="request in ownedRequests"
            :key="request.uuid"
            :request="request"
          />
        </div>
        <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
          {{ t('feedback.noOwnedRequests') }}
        </PText>
      </PTab>

      <PTab :title="t('feedback.invitedRequests')">
        <template #prepend>
          <Badge :count="newFeedbackCount" :max="999" />
        </template>

        <div
          v-if="invitedPending"
          class="flex items-center justify-center py-8"
        >
          <PLoading class="text-primary" :size="20" />
        </div>
        <div
          v-else-if="invitedError"
          class="flex flex-col items-center gap-4 py-8"
        >
          <PText as="p" class="text-center text-danger" responsive>
            {{ t('feedback.getError') }}
          </PText>
          <PButton
            color="gray"
            :icon-start="PeyRetryIcon"
            @click="invitedRefresh"
          >
            {{ t('common.retry') }}
          </PButton>
        </div>
        <div
          v-else-if="invitedRequests?.length"
          class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
        >
          <FeedbackCard
            v-for="request in invitedRequests"
            :key="request.uuid"
            :request="request"
          />
        </div>
        <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
          {{ t('feedback.noInvitedRequests') }}
        </PText>
      </PTab>
    </PTabs>
  </div>
</template>
