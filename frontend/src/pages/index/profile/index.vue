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

      <div class="flex items-center gap-2">
        <NuxtLink :to="{ name: 'profile-edit' }">
          <PIconButton class="shrink-0" :icon="PeyEditIcon" tabindex="-1" />
        </NuxtLink>

        <PIconButton
          class="shrink-0"
          color="danger"
          :icon="PeyLogoutIcon"
          @click="logout"
        />
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
          <ProfileDetail :profile="profile" />
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
  PIconButton,
} from '@pey/core';
import { PeyEditIcon, PeyLogoutIcon, PeyRetryIcon } from '@pey/icons';
import ProfileDetail from '~/components/profile/ProfileDetail.vue';
import UserTimeline from '~/components/timeline/UserTimeline.vue';

definePageMeta({ name: 'profile' });

const { t } = useI18n();
const { data: profile, isPending, error, refetch } = useGetProfile();
const logout = useLogout();

useHead({
  title: profile.value?.name,
});
</script>
