<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-user text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ profile?.name }}
        </PHeading>
      </div>
    </div>

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

    <div v-else-if="profile">
      <PTabs class="pt-4">
        <PTab :title="t('common.details')">
          <PBox
            class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10"
          >
            <ProfileDetail :profile="profile" :is-current-user="true" />
          </PBox>
        </PTab>
        <PTab :title="t('common.timeline')">
          <UserTimeline :user-id="profile.uuid" />
        </PTab>
      </PTabs>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  PBox,
  PButton,
  PHeading,
  PLoading,
  PText,
  PTabs,
  PTab,
} from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import ProfileDetail from '~/components/profile/ProfileDetail.vue';
import UserTimeline from '~/components/timeline/UserTimeline.vue';

definePageMeta({ name: 'profile' });

const { t } = useI18n();
const { data: profile, isPending, error, refetch } = useGetProfile();

useHead({
  title: profile.value?.name,
});
</script>
