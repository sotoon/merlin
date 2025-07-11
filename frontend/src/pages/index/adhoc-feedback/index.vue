<script setup lang="ts">
import { PButton, PLoading, PText, PTabs, PTab } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import { useRouteQuery } from '@vueuse/router';

definePageMeta({ name: 'adhoc-feedback' });

const { t } = useI18n();
const { data: profile } = useGetProfile();

const tabOptions = ['received', 'sent'] as const;
const tabFilter = useRouteQuery<'received' | 'sent'>('tab', 'received');

const currentTabIndex = computed(() => {
  return tabOptions.indexOf(tabFilter.value as any) || 0;
});

const handleTabChange = (index: number) => {
  tabFilter.value = tabOptions[index];
};

const {
  data: adhocEntries,
  isPending: adhocPending,
  isError: adhocError,
  refetch: adhocRefresh,
} = useGetAdhocFeedbackEntries();

const receivedEntries = computed(() => {
  if (!adhocEntries.value || !profile.value) return [];
  return adhocEntries.value.filter(
    (entry) => entry.receiver.uuid === profile.value?.uuid,
  );
});

const sentEntries = computed(() => {
  if (!adhocEntries.value || !profile.value) return [];
  return adhocEntries.value.filter(
    (entry) => entry.sender.uuid === profile.value?.uuid,
  );
});

const unreadReceivedEntriesCount = computed(() => {
  if (!receivedEntries.value) return 0;
  return receivedEntries.value.filter((entry) => !entry.note.read_status)
    .length;
});
</script>

<template>
  <div>
    <PTabs :model-value="currentTabIndex" @update:model-value="handleTabChange">
      <PTab :title="t('feedback.received')">
        <template #prepend>
          <Badge :count="unreadReceivedEntriesCount" :max="999" />
        </template>

        <div v-if="adhocPending" class="flex items-center justify-center py-8">
          <PLoading class="text-primary" :size="20" />
        </div>
        <div
          v-else-if="adhocError"
          class="flex flex-col items-center gap-4 py-8"
        >
          <PText as="p" class="text-center text-danger" responsive>
            {{ t('feedback.getError') }}
          </PText>
          <PButton
            color="gray"
            :icon-start="PeyRetryIcon"
            @click="adhocRefresh"
          >
            {{ t('common.retry') }}
          </PButton>
        </div>
        <div
          v-else-if="receivedEntries?.length"
          class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
        >
          <FeedbackAdhocCard
            v-for="entry in receivedEntries"
            :key="entry.uuid"
            :entry="entry"
          />
        </div>
        <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
          {{ t('feedback.noAdhocFeedback') }}
        </PText>
      </PTab>

      <PTab :title="t('feedback.sent')">
        <div v-if="adhocPending" class="flex items-center justify-center py-8">
          <PLoading class="text-primary" :size="20" />
        </div>
        <div
          v-else-if="adhocError"
          class="flex flex-col items-center gap-4 py-8"
        >
          <PText as="p" class="text-center text-danger" responsive>
            {{ t('feedback.getError') }}
          </PText>
          <PButton
            color="gray"
            :icon-start="PeyRetryIcon"
            @click="adhocRefresh"
          >
            {{ t('common.retry') }}
          </PButton>
        </div>
        <div
          v-else-if="sentEntries?.length"
          class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
        >
          <FeedbackAdhocCard
            v-for="entry in sentEntries"
            :key="entry.uuid"
            :entry="entry"
          />
        </div>
        <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
          {{ t('feedback.noAdhocFeedback') }}
        </PText>
      </PTab>
    </PTabs>
  </div>
</template>
