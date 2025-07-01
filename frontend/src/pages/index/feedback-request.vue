<script setup lang="ts">
import { PHeading, PIconButton } from '@pey/core';
import { PeyPlusIcon } from '@pey/icons';

useHead({ title: 'درخواست فیدبک' });

const { t } = useI18n();
const route = useRoute();

const showHeader = computed(() => route.name === 'feedback-request');
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
        <i class="i-mdi-account-supervisor text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('common.feedbackRequest') }}
        </PHeading>
      </div>

      <NuxtLink :to="{ name: 'feedback-request-new' }">
        <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
      </NuxtLink>
    </div>

    <NuxtPage />
  </div>
</template>
