<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-user text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ user?.name }}
        </PHeading>
      </div>
    </div>

    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('user.getUserError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <div v-else-if="user">
      <PTabs v-if="isManager" class="pt-4">
        <PTab :title="t('common.details')">
          <PBox
            class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10"
          >
            <ProfileDetail :profile="user" />
          </PBox>
        </PTab>
        <PTab :title="t('common.timeline')">
          <PBox
            class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10"
          >
            <UserTimeline :user-id="userId" />
          </PBox>
        </PTab>
      </PTabs>

      <PBox
        v-else
        class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10"
      >
        <ProfileDetail :profile="user" />
      </PBox>
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
import { useRoute } from 'vue-router';
import { useGetUser } from '~/composables/users/useGetUsers';
import { useGetProfile } from '~/composables/users/useGetProfile';
import ProfileDetail from '~/components/profile/ProfileDetail.vue';
import UserTimeline from '~/components/timeline/UserTimeline.vue';

definePageMeta({ name: 'user-detail' });

const { t } = useI18n();
const route = useRoute();
const userId = computed(() => route.params.id as string);

const {
  data: user,
  isPending: pending,
  error,
  refetch: refresh,
} = useGetUser(userId);
const { data: currentUserProfile } = useGetProfile();

const isManager = computed(() => {
  if (!currentUserProfile.value || !user.value?.leader) {
    return false;
  }
  return currentUserProfile.value.name === user.value.leader;
});

useHead({
  title: user.value?.name,
});
</script>
