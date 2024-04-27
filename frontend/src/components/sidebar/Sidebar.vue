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
          <li>
            <SidebarLinkGroup :title="t('common.notes')">
              <li v-for="link in notesLinks" :key="link.label">
                <SidebarLink v-bind="link" />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup :title="t('common.personal')">
              <li>
                <SidebarLink
                  :badge-count="newMessagesCount"
                  icon="💬"
                  :label="t('common.messages')"
                  :to="{ name: 'messages' }"
                />
              </li>

              <li>
                <SidebarLink
                  icon="📋"
                  :label="t('common.templates')"
                  :to="{ name: 'templates' }"
                />
              </li>

              <li v-if="isLeader">
                <SidebarLink
                  icon="👥"
                  :label="t('common.myTeam')"
                  :to="{ name: 'my-team' }"
                />
              </li>
            </SidebarLinkGroup>
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

import { getNotesLinks } from '~/components/sidebar/SidebarLinks';

const { t } = useI18n();
const logout = useLogout();
const { data: users } = useGetMyTeam();
const { data: messages } = useGetNotes({ retrieveMentions: true });

const notesLinks = computed(() => getNotesLinks(t));
const isLeader = computed(() => Boolean(users.value?.length));
const newMessagesCount = computed(
  () => messages.value?.filter((message) => !message.read_status).length,
);
</script>
