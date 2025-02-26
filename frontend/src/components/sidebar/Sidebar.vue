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
            <SidebarLinkGroup :title="t('common.forms')">
              <li>
                <!-- // TODO: set badge count for incomplete forms -->
                <SidebarLink
                  icon="i-mdi-form"
                  :label="t('common.forms')"
                  :to="{ name: 'forms' }"
                />
              </li>

              <li>
                <SidebarLink
                  icon="i-mdi-chart-bar"
                  :label="t('common.results')"
                  :to="{ name: 'my-forms' }"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup :title="t('common.personal')">
              <li>
                <SidebarLink
                  :badge-count="newMessagesCount"
                  icon="i-mdi-message-text"
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

              <li v-if="isTeamLeader">
                <SidebarLink
                  icon="i-mdi-account-group"
                  :label="t('common.myTeam')"
                  :to="{ name: 'my-team' }"
                />
              </li>
            </SidebarLinkGroup>
          </li>
        </ul>
      </PScrollbar>

      <div class="flex flex-col space-y-2 border-t border-gray-10 pt-2">
        <SidebarLink
          external
          icon="i-mdi-help-circle"
          :label="t('common.performanceManagementGuide')"
          :to="GUIDE_DRIVE_LINK"
        />

        <SidebarProfileLink />
      </div>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';

import { getNotesLinks } from '~/components/sidebar/SidebarLinks';

const { t } = useI18n();
const { data: messages } = useGetNotes({ retrieveMentions: true });
const isTeamLeader = useIsTeamLeader();

// TODO: filter out templates in the backend
const messagesWithoutTemplates = computed(
  () => messages.value?.filter(({ type }) => type !== NOTE_TYPE.template) || [],
);
const notesLinks = computed(() => getNotesLinks(t));
const newMessagesCount = computed(
  () =>
    messagesWithoutTemplates.value?.filter((message) => !message.read_status)
      .length,
);
</script>
