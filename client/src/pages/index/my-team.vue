<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <PHeading level="h1" responsive>
        {{ t('common.myTeam') }}
      </PHeading>
    </div>

    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('user.getUsersError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <UserList v-else-if="users?.length" :users="users" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('user.noUser') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'my-team' });

const { t } = useI18n();
useHead({ title: t('common.myTeam') });
const {
  data: users,
  pending,
  error,
  refresh,
} = useGetMyTeam({ dedupe: 'defer' });

watch(users, () => {
  if (users.value && !users.value.length) {
    navigateTo({ name: 'home', replace: true });
  }
});
</script>
