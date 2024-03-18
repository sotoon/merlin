<template>
  <div
    v-if="noteType"
    class="space-y-4 divide-y divide-gray-20 px-4 py-8 lg:px-8 lg:pt-10"
  >
    <PHeading level="h1" responsive>
      {{ noteTitles[noteType] }}
    </PHeading>

    <NoteList :type="noteType" />
  </div>
</template>

<script lang="ts" setup>
import { PHeading } from '@pey/core';

const { t } = useI18n();
const {
  params: { type },
} = useRoute();

const noteType = computed(() => {
  if (typeof type === 'string' && type in NOTE_TYPE && type !== 'template') {
    return NOTE_TYPE[type as Exclude<keyof typeof NOTE_TYPE, 'template'>];
  }

  return null;
});
const noteTitles = computed(() => ({
  [NOTE_TYPE.goal]: t('note.noteTitle', { type: t('common.goals') }),
  [NOTE_TYPE.meeting]: t('note.noteTitle', { type: t('common.meetings') }),
  [NOTE_TYPE.message]: t('note.noteTitle', { type: t('common.messages') }),
  [NOTE_TYPE.personal]: t('common.personalNotes'),
  [NOTE_TYPE.proposal]: t('note.noteTitle', { type: t('common.proposal') }),
  [NOTE_TYPE.task]: t('note.noteTitle', { type: t('common.tasks') }),
}));

useHead({
  title: noteType.value && noteTitles.value[noteType.value],
});

onMounted(() => {
  if (!noteType.value) {
    navigateTo('/notes/', { replace: true });
  }
});
</script>
