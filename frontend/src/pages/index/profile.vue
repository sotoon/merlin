<template>
  <PBox class="max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('profile.getProfileError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NuxtPage v-else-if="profile" :profile="profile" />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const { t } = useI18n();
const { data: profile, isLoading, error, refetch } = useGetProfile();
</script>
