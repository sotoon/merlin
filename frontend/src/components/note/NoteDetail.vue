<template>
  <div class="px-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <i
          class="mb-3 me-4 inline-block align-middle text-h1 text-primary"
          :class="NOTE_TYPE_ICON[note.type]"
        />

        <PText responsive variant="title" weight="bold">
          {{ note.title }}
        </PText>
      </div>

      <div class="flex flex-col items-center gap-4 md:mt-2 md:flex-row">
        <slot name="actions" />
      </div>
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

    <div v-if="note.linked_notes.length" class="mt-8">
      <PHeading :lvl="4" responsive>
        {{ t('note.relatedNotes') }}
      </PHeading>

      <div class="mt-4 flex flex-wrap gap-2">
        <NoteLinkChip
          v-for="linkedNoteId in note.linked_notes"
          :key="linkedNoteId"
          :note-id="linkedNoteId"
        />
      </div>
    </div>

    <div
      v-if="
        NOTES_WITH_SUMMARY.includes(note.type) &&
        note.access_level.can_view_summary
      "
      class="mt-8"
    >
      <NoteSummary :note="note" />
    </div>

    <div class="mt-8">
      <NoteFeedbacks :note="note" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PChip, PHeading, PText, PTooltip } from '@pey/core';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { data: users } = useGetUsers();

const mentionedUsers = computed(() =>
  users.value?.filter(({ email }) =>
    props.note.mentioned_users.includes(email),
  ),
);
</script>
