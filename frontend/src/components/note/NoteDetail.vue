<template>
  <div class="px-4">
    <div class="flex items-center justify-between gap-4">
      <PText responsive variant="title" weight="bold">
        {{ note.title }}
      </PText>

      <PIconButton
        v-if="note.access_level.can_edit"
        class="shrink-0"
        :icon="PeyEditIcon"
        type="button"
        @click="navigateTo({ name: 'note-edit' })"
      />

      <PChip
        v-if="!note.access_level.can_edit && note.type !== 'Template'"
        :label="noteTypeLabel[note.type]"
      />
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.lastEdit') }}:
        <PTooltip>
          <PText class="text-gray-70" variant="caption1">
            {{ formatTimeAgo(new Date(note.date_updated), 'fa-IR') }}
          </PText>

          <template #content>
            <PText dir="ltr" variant="caption1">
              {{ new Date(note.date_updated).toLocaleString('fa-IR') }}
            </PText>
          </template>
        </PTooltip>
      </PText>

      <PText
        v-if="!note.access_level.can_edit"
        as="p"
        class="text-gray-50"
        variant="caption1"
      >
        {{ t('note.writer') }}:
        <NuxtLink
          class="text-primary hover:underline"
          :to="{
            name: 'notes',
            params: { type: '-' },
            query: { user: note.owner },
          }"
        >
          {{ note.owner_name }}
        </NuxtLink>
      </PText>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{
          note.type === NOTE_TYPE.meeting
            ? t('note.meetingDate')
            : t('common.date')
        }}:
        <PText class="text-gray-70" variant="caption1">
          {{ new Date(note.date).toLocaleDateString('fa-IR') }}
        </PText>
      </PText>

      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.period') }}:
        <PText class="text-gray-70" variant="caption1">
          {{ EVALUATION_PERIODS[note.period] || '' }}
          {{ note.year.toLocaleString('fa-IR', { useGrouping: false }) }}
        </PText>
      </PText>
    </div>

    <article class="mt-4 py-4">
      <EditorContent :content="note.content" />
    </article>

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

    <div v-if="linkedNotes?.length" class="mt-8">
      <PHeading :lvl="4" responsive>
        {{ t('note.relatedNotes') }}
      </PHeading>

      <div class="mt-4 flex flex-wrap gap-2">
        <NuxtLink
          v-for="linkedNote in linkedNotes"
          :key="linkedNote.uuid"
          class="*:cursor-pointer"
          :to="linkedNote.to"
        >
          <PChip
            color="primary"
            :icon="PeyLinkIcon"
            :label="linkedNote.title"
            size="small"
          />
        </NuxtLink>
      </div>
    </div>

    <div v-if="NOTES_WITH_SUMMARY.includes(note.type)" class="mt-8">
      <NoteSummary :note="note" />
    </div>

    <div class="mt-8">
      <NoteFeedbacks :note="note" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PChip, PHeading, PIconButton, PText, PTooltip } from '@pey/core';
import { PeyEditIcon, PeyLinkIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { data: users } = useGetUsers();
const { data: myNotes } = useGetNotes();
const { data: mentionedNotes } = useGetNotes({ retrieveMentions: true });

const mentionedUsers = computed(() =>
  users.value?.filter(({ email }) =>
    props.note.mentioned_users.includes(email),
  ),
);
const linkedNotes = computed(() => [
  ...(myNotes.value
    ?.filter(({ uuid }) => props.note.linked_notes.includes(uuid))
    .map((note) => ({
      ...note,
      to:
        note.type === NOTE_TYPE.template
          ? {
              name: 'template',
              params: { id: note.uuid },
            }
          : {
              name: 'note',
              params: {
                type: NOTE_TYPE_ROUTE_PARAM[note.type],
                id: note.uuid,
              },
            },
    })) || []),
  ...(mentionedNotes.value
    ?.filter(({ uuid }) => props.note.linked_notes.includes(uuid))
    .map((note) => ({
      ...note,
      to: {
        name: 'note',
        params: {
          type: '-',
          id: note.uuid,
        },
      },
    })) || []),
]);

const noteTypeLabel = computed(() => ({
  [NOTE_TYPE.goal]: t('noteType.goal'),
  [NOTE_TYPE.meeting]: t('noteType.meeting'),
  [NOTE_TYPE.message]: t('noteType.message'),
  [NOTE_TYPE.personal]: t('noteType.personal'),
  [NOTE_TYPE.proposal]: t('noteType.proposal'),
  [NOTE_TYPE.task]: t('noteType.task'),
}));
</script>
