<script setup lang="ts">
import { PButton, PLoading, PText, PTabs, PTab } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'feedback-request' });

const { t } = useI18n();

const {
  data: ownedRequests,
  isPending: ownedPending,
  isError: ownedError,
  refetch: ownedRefresh,
} = useGetFeedbackRequestsOwned();
const {
  data: invitedRequests,
  isPending: invitedPending,
  isError: invitedError,
  refetch: invitedRefresh,
} = useGetFeedbackRequestsInvited();
</script>

<template>
  <div>
    <PTabs>
      <PTab :title="t('feedback.ownedRequests')">
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
          <FeedbackRequestCard
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
          <FeedbackRequestCard
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
