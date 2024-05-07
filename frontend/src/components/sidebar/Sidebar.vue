<template>
  <nav class="flex h-full w-60 flex-col overflow-hidden py-4">
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
                  icon="mdi:message-text"
                  :label="t('common.messages')"
                  :to="{ name: 'messages' }"
                />
              </li>

              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.template]"
                  :label="t('common.templates')"
                  :to="{ name: 'templates' }"
                />
              </li>

              <li v-if="isLeader">
                <SidebarLink
                  icon="mdi:account-group"
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
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';

import { getNotesLinks } from '~/components/sidebar/SidebarLinks';

const { t } = useI18n();
const { data: users } = useGetMyTeam();
const { data: messages } = useGetNotes({ retrieveMentions: true });

// TODO: filter out templates in the backend
const messagesWithoutTemplates = computed(
  () => messages.value?.filter(({ type }) => type !== NOTE_TYPE.template) || [],
);
const notesLinks = computed(() => getNotesLinks(t));
const isLeader = computed(() => Boolean(users.value?.length));
const newMessagesCount = computed(
  () =>
    messagesWithoutTemplates.value?.filter((message) => !message.read_status)
      .length,
);
</script>
