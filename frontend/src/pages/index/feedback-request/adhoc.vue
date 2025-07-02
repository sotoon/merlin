<script lang="ts" setup>
import { PBox, PLoading, PButton, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const { t } = useI18n();

const {
  data: entries,
  isPending,
  error,
  refetch: refreshEntries,
} = useGetAdhocFeedbackEntries();

useHead({
  title: () => t('feedback.adhocFeedback'),
});
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <div v-if="isPending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('feedback.getError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refreshEntries">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NuxtPage v-else-if="entries" :entries="entries" />
  </PBox>
</template>
