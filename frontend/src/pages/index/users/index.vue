<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <PHeading level="h1" responsive>
          {{ t('common.users') }}
        </PHeading>
      </div>
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

    <div v-else class="py-4">
      <PTable :data="users" :items-per-page="10" paginate searchable>
        <PTableColumn type="index" />
        <PTableColumn label="نام" prop="name" />
        <PTableColumn label="ایمیل" prop="email" />
        <PTableColumn label="تیم" prop="team" />
        <PTableColumn>
          <template #default="{ row }">
            <NuxtLink
              :to="{ name: 'user-detail', params: { id: (row as any).uuid } }"
            >
              <PButton size="small" color="primary">
                {{ t('common.details') }}
              </PButton>
            </NuxtLink>
          </template>
        </PTableColumn>
      </PTable>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  PButton,
  PHeading,
  PLoading,
  PText,
  PTable,
  PTableColumn,
} from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'user-list' });

const { t } = useI18n();
const {
  data: users,
  isPending: pending,
  error,
  refetch: refresh,
} = useGetUsers();

useHead({
  title: t('common.users'),
});
</script>
