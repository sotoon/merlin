<template>
  <nav
    class="flex h-full w-60 flex-col overflow-hidden bg-white py-4 shadow-lg"
  >
    <NuxtLink class="pb-4 pt-2 shadow" to="/">
      <PText as="p" class="text-center" weight="bold" variant="h4">
        {{ t('common.appName') }}
      </PText>
    </NuxtLink>

    <div class="flex grow flex-col overflow-hidden px-2">
      <PScrollbar class="-mx-2 grow px-2 py-4">
        <ul class="space-y-6">
          <li v-for="linkGroup in sidebarLinks" :key="linkGroup.title">
            <SidebarLinkGroup v-bind="linkGroup" />
          </li>
        </ul>
      </PScrollbar>

      <hr class="mb-2 border-gray-10" />

      <SidebarProfileLink />

      <button
        class="flex items-center gap-3 rounded px-4 py-2 hover:bg-gray-00 focus:bg-gray-00"
        type="button"
        @click="logout"
      >
        <PeyLogoutIcon class="text-primary" />
        <PText variant="caption1">
          {{ t('common.logout') }}
        </PText>
      </button>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';
import { PeyLogoutIcon } from '@pey/icons';

import getSidebarLinks from '~/components/sidebar/SidebarLinks';

const { t } = useI18n();
const logout = useLogout();
const { data: users } = useGetMyTeam();

const isLeader = computed(() => Boolean(users.value?.length));
const sidebarLinks = computed(() =>
  getSidebarLinks(t).map((group) => ({
    ...group,
    links: group.links.filter((link) => !link.leaderLink || isLeader.value),
  })),
);
</script>
