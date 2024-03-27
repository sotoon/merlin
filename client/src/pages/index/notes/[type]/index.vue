<template>
  <div v-if="noteType" class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <PHeading level="h1" responsive>
        {{ noteTitles[noteType] }}
      </PHeading>

      <NuxtLink :to="`/notes/${type}/new`">
        <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
      </NuxtLink>
    </div>

    <NoteList :type="noteType" />
  </div>
</template>

<script lang="ts" setup>
import { PHeading, PIconButton } from '@pey/core';
import { PeyPlusIcon } from '@pey/icons';

const props = defineProps<{ noteType: Exclude<NoteType, 'Template'> }>();

const { t } = useI18n();
const {
  params: { type },
} = useRoute();

const noteTitles = computed(() => ({
  [NOTE_TYPE.goal]: t('note.noteTitle', { type: t('common.goals') }),
  [NOTE_TYPE.meeting]: t('note.noteTitle', { type: t('common.meetings') }),
  [NOTE_TYPE.message]: t('note.noteTitle', { type: t('common.messages') }),
  [NOTE_TYPE.personal]: t('common.personalNotes'),
  [NOTE_TYPE.proposal]: t('note.noteTitle', { type: t('common.proposal') }),
  [NOTE_TYPE.task]: t('note.noteTitle', { type: t('common.tasks') }),
}));

useHead({
  title: noteTitles.value[props.noteType],
});
</script>
