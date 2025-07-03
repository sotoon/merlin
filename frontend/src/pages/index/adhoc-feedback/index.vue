<script setup lang="ts">
import { PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'adhoc-feedback' });

const { t } = useI18n();

const {
  data: adhocEntries,
  isPending: adhocPending,
  isError: adhocError,
  refetch: adhocRefresh,
} = useGetAdhocFeedbackEntries();
</script>

<template>
  <div>
    <div v-if="adhocPending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>
    <div v-else-if="adhocError" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('feedback.getError') }}
      </PText>
      <PButton color="gray" :icon-start="PeyRetryIcon" @click="adhocRefresh">
        {{ t('common.retry') }}
      </PButton>
    </div>
    <div
      v-else-if="adhocEntries?.length"
      class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
    >
      <FeedbackAdhocCard
        v-for="entry in adhocEntries"
        :key="entry.uuid"
        :entry="entry"
      />
    </div>
    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('feedback.noAdhocFeedback') }}
    </PText>
  </div>
</template>
