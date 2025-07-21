<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div v-if="isPending" class="flex items-center justify-center py-8">
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

    <ProfileDetail v-else-if="profile" :profile="profile" is-current-user />
  </div>
</template>

<script lang="ts" setup>
import { PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'profile' });

const { t } = useI18n();
const { data: profile, isPending, error, refetch } = useGetProfile();
</script>
