<script lang="ts" setup>
import { PBox, PLoading, PButton, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import {
  useGetFeedbackRequest,
  useGetFeedbackRequestEntries,
} from '~/composables/useFeedbackServices';

const route = useRoute();
const { t } = useI18n();
const requestId = route.params.requestId as string;

const {
  data: request,
  isPending: requestPending,
  error: requestError,
  refetch: refreshRequest,
} = useGetFeedbackRequest(requestId);
const {
  data: entries,
  isPending: entriesPending,
  error: entriesError,
  refetch: refreshEntries,
} = useGetFeedbackRequestEntries(requestId);

const pending = computed(() => requestPending.value || entriesPending.value);
const error = computed(() => requestError.value || entriesError.value);

const refreshAll = () => {
  refreshRequest();
  refreshEntries();
};

useHead({
  title: () => (request.value as any)?.title || t('common.feedbackRequest'),
});
</script>
<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('feedback.getError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refreshAll">
        {{ t('common.retry') }}
      </PButton>
    </div>
    <NuxtPage
      v-else-if="request && entries"
      :request="request"
      :entries="entries"
    />
  </PBox>
</template>
