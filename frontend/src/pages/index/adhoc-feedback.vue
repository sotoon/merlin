<script setup lang="ts">
import { PHeading, PIconButton } from '@pey/core';
import { PeyPlusIcon } from '@pey/icons';

useHead({ title: 'فیدبک مستقیم' });

const { t } = useI18n();
const route = useRoute();

const showHeader = computed(() => route.name === 'adhoc-feedback');
</script>

<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      v-if="showHeader"
      :class="[
        'flex items-center justify-between gap-2 border-b border-gray-20 pb-4',
      ]"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-comment-quote-outline text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('feedback.adhocFeedback') }}
        </PHeading>
      </div>

      <div class="flex items-center gap-2">
        <NuxtLink :to="{ name: 'adhoc-feedback-new' }">
          <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
        </NuxtLink>
      </div>
    </div>

    <NuxtPage />
  </div>
</template>
