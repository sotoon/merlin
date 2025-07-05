<script lang="ts" setup>
import { PLoading, PTabs, PTab } from '@pey/core';

definePageMeta({ name: 'one-on-one' });
defineProps<{ users: User[]; pendingUsers: boolean }>();

const { t } = useI18n();

const { data: profile, isLoading } = useGetProfile();
</script>

<template>
  <div>
    <PTabs v-if="users?.length">
      <PTab :title="t('common.myTeam')">
        <ul
          class="grid grid-cols-1 gap-2 py-4 md:grid-cols-2 md:gap-3 xl:grid-cols-3"
        >
          <li v-for="user in users" :key="user.uuid">
            <NuxtLink
              :to="{
                name: 'one-on-one-userId',
                params: { userId: user.uuid },
              }"
            >
              <UserCard :user="user" />
            </NuxtLink>
          </li>
        </ul>
      </PTab>
      <PTab :title="t('oneOnOne.withManager')">
        <div v-if="isLoading" class="flex items-center justify-center py-8">
          <PLoading class="text-primary" :size="20" />
        </div>
        <NoteOneOnOneList
          v-else
          :user-id="profile?.uuid || ''"
          :username="profile?.name || ''"
        />
      </PTab>
    </PTabs>

    <div v-else>
      <div v-if="isLoading" class="flex items-center justify-center py-8">
        <PLoading class="text-primary" :size="20" />
      </div>
      <NoteOneOnOneList
        v-else
        :user-id="profile?.uuid || ''"
        :username="profile?.name || ''"
      />
    </div>
  </div>
</template>
