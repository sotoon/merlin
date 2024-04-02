<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<!-- eslint-disable vue/no-v-html -->
<template>
  <div class="px-4">
    <div class="flex items-center justify-between gap-4">
      <PHeading responsive>
        {{ note.title }}
      </PHeading>

      <PIconButton
        v-if="note.access_level.can_edit"
        class="shrink-0"
        :icon="PeyEditIcon"
        type="button"
        @click="navigateTo({ name: 'note-edit' })"
      />
    </div>

    <div class="py-4" v-html="note.content" />

    <div v-if="mentionedUsers?.length" class="mt-4">
      <PHeading :lvl="4" responsive>
        {{ t('note.mentionedUsers') }}
      </PHeading>

      <div class="mt-4 flex flex-wrap gap-2">
        <PChip
          v-for="user in mentionedUsers"
          :key="user.uuid"
          :label="`${user.name} (${user.email})`"
          size="small"
        />
      </div>
    </div>

    <div v-if="NOTES_WITH_SUMMARY.includes(note.type)" class="mt-8">
      <template v-if="note.summary">
        <div class="flex items-center justify-between gap-4">
          <PHeading :lvl="3" responsive>
            {{ t('note.summary') }}
          </PHeading>

          <PIconButton
            v-if="note.access_level.can_write_summary"
            class="shrink-0"
            :icon="PeyEditIcon"
            type="button"
            @click="navigateTo({ name: 'note-summary' })"
          />
        </div>

        <div class="py-4" v-html="note.summary" />
      </template>

      <PButton
        v-else-if="note.access_level.can_write_summary"
        :icon-start="PeyPlusIcon"
        variant="ghost"
        @click="navigateTo({ name: 'note-summary' })"
      >
        {{ t('note.writeSummary') }}
      </PButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PChip, PHeading, PIconButton } from '@pey/core';
import { PeyEditIcon, PeyPlusIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { data: users } = useGetUsers();

const mentionedUsers = computed(() =>
  users.value?.filter(({ email }) =>
    props.note.mentioned_users.includes(email),
  ),
);
</script>
