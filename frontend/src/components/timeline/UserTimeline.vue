<template>
  <div class="space-y-4">
    <div v-if="isPending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('timeline.getTimelineError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <div v-else>
      <!-- User Level Card -->
      <UserLevelCard :level="data?.pages?.[0]?.level" />

      <!-- Timeline Controls -->
      <PBox class="mb-6 flex flex-wrap items-center gap-8 bg-white p-4">
        <div class="flex flex-wrap items-center gap-2">
          <i class="i-mdi-timeline-clock text-h3 text-gray-50" />
          <PText variant="body" class="text-gray-90">
            {{ t('common.timeline') }}
          </PText>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <PeyFilterIcon class="text-gray-50" />
          <TimelineEventTypeFilter v-model="selectedEventTypes" />
        </div>
      </PBox>

      <!-- Timeline -->
      <div class="relative">
        <!-- Timeline line -->
        <div class="absolute bottom-0 left-6 top-0 w-0.5 bg-gray-20"></div>

        <!-- Timeline events -->
        <div class="space-y-6">
          <div
            v-for="(page, pageIndex) in data?.pages"
            :key="pageIndex"
            class="space-y-6"
          >
            <div
              v-for="event in getFilteredEvents(page.results)"
              :key="event.id"
              class="relative flex items-start gap-4"
            >
              <!-- Timeline dot and icon -->
              <div
                class="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border-2 border-primary bg-white shadow-sm"
              >
                <i
                  :class="getEventIcon(event.event_type)"
                  class="text-h2 text-primary"
                />
              </div>

              <!-- Event content -->
              <div class="min-w-0 flex-1">
                <div
                  class="rounded-lg border border-gray-20 bg-white p-4 shadow-sm"
                >
                  <div class="mb-2 flex items-center justify-between">
                    <PText class="font-medium text-gray-90" variant="body">
                      {{ getEventTitle(event.event_type) }}
                    </PText>
                    <PText class="text-gray-60" variant="caption1">
                      {{ formatDate(event.effective_date) }}
                    </PText>
                  </div>

                  <PText
                    class="whitespace-pre-line text-gray-80"
                    variant="body"
                  >
                    {{ event.summary_text }}
                  </PText>

                  <div v-if="event.object_url" class="mt-3">
                    <NuxtLink
                      :to="event.object_url"
                      class="hover:text-primary-dark inline-flex items-center gap-1 text-primary transition-colors"
                    >
                      <PText variant="caption1">{{
                        t('timeline.viewDetails')
                      }}</PText>
                      <i class="i-mdi-arrow-left text-sm" />
                    </NuxtLink>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Load more button -->
        <div v-if="hasNextPage" class="flex justify-center pt-6">
          <PButton
            :loading="isFetchingNextPage"
            color="gray"
            @click="fetchNextPage"
          >
            {{ t('timeline.loadMore') }}
          </PButton>
        </div>

        <!-- No more data -->
        <div
          v-else-if="data?.pages && data.pages.length > 0"
          class="flex justify-center pt-6"
        >
          <PText class="text-gray-60" variant="caption1">
            {{ t('timeline.noMoreEvents') }}
          </PText>
        </div>

        <!-- Empty state -->
        <div v-else class="flex flex-col items-center gap-4 py-8">
          <i class="text-4xl i-mdi-timeline-clock text-gray-40" />
          <PText class="text-center text-gray-60" responsive>
            {{ t('timeline.noEvents') }}
          </PText>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PLoading, PText, PBox } from '@pey/core';
import { PeyRetryIcon, PeyFilterIcon } from '@pey/icons';
import { useGetUserTimeline } from '~/composables/users/useGetUserTimeline';
import UserLevelCard from './UserLevelCard.vue';
import TimelineEventTypeFilter from './TimelineEventTypeFilter.vue';

const props = defineProps<{
  userId: string;
}>();

const { t } = useI18n();
const {
  data,
  isPending,
  error,
  refetch,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useGetUserTimeline(props.userId);

// Filter state
const selectedEventTypes = ref<string[]>([]);

// Filter events based on selected event types
const getFilteredEvents = (events: any[]) => {
  if (!selectedEventTypes.value.length) {
    return events;
  }
  return events.filter((event) =>
    selectedEventTypes.value.includes(event.event_type),
  );
};

const getEventIcon = (eventType?: string) => {
  switch (eventType) {
    case 'SENIORITY_CHANGE':
      return 'i-mdi-account-arrow-up';
    case 'PAY_CHANGE':
      return 'i-mdi-currency-usd';
    case 'BONUS_PAYOUT':
      return 'i-mdi-gift';
    case 'EVALUATION':
      return 'i-mdi-clipboard-check';
    case 'MAPPING':
      return 'i-mdi-account-switch';
    case 'TITLE_CHANGE':
      return 'i-mdi-badge-account';
    case 'STOCK_GRANT':
      return 'i-mdi-chart-line';
    case 'NOTICE':
      return 'i-mdi-bell';
    case 'LADDER_CHANGED':
      return 'i-mdi-account-arrow-up';
    default:
      return 'i-mdi-circle';
  }
};

const getEventTitle = (eventType?: string) => {
  switch (eventType) {
    case 'SENIORITY_CHANGE':
      return t('timeline.seniorityChange');
    case 'PAY_CHANGE':
      return t('timeline.payChange');
    case 'BONUS_PAYOUT':
      return t('timeline.bonusPayout');
    case 'EVALUATION':
      return t('timeline.evaluation');
    case 'MAPPING':
      return t('timeline.mapping');
    case 'TITLE_CHANGE':
      return t('timeline.titleChange');
    case 'STOCK_GRANT':
      return t('timeline.stockGrant');
    case 'NOTICE':
      return t('timeline.notice');
    case 'LADDER_CHANGED':
      return t('timeline.ladderChanged');
    default:
      return t('timeline.unknownEvent');
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};
</script>
