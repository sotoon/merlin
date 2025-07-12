<script lang="ts" setup>
import { PButton, PHeading, PLoading, PText, PIconButton } from '@pey/core';
import { PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

useHead({ title: 'یک به یک' });

const { t } = useI18n();
const route = useRoute();

const { data: users, pending, error, refresh } = useGetMyTeam();

const hasAccessCreateOneOnOne = computed(
  () => route.name === 'one-on-one-userId' && !!users.value?.length,
);

const shouldHideTitle = computed(
  () =>
    route.name === 'one-on-one-edit' ||
    route.name === 'one-on-one-id' ||
    route.name === 'one-on-one-comment' ||
    route.name === 'one-on-one-new',
);

const user = computed(() =>
  users.value?.find((user) => user.uuid === route.params.userId),
);
</script>

<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      :class="[
        'flex items-center justify-between gap-2 border-gray-20',
        {
          'border-b pb-4': !shouldHideTitle,
        },
      ]"
    >
      <div v-if="!shouldHideTitle" class="flex items-center gap-4">
        <i class="i-mdi-account-supervisor text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('common.oneOnOne') }} {{ user ? `با ${user.name}` : '' }}
        </PHeading>
      </div>

      <NuxtLink
        v-if="hasAccessCreateOneOnOne"
        :to="{
          name: 'one-on-one-new',
          params: { userId: route.params.userId },
        }"
      >
        <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
      </NuxtLink>
    </div>

    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('oneOnOne.getUsersError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NuxtPage v-if="!pending" :users="users || []" :pending-users="pending" />
  </div>
</template>
