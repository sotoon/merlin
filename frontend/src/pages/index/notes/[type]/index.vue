<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <PHeading level="h1" responsive>
        {{ noteTitle }}
      </PHeading>

      <NuxtLink v-if="!isUser" :to="{ name: 'note-create' }">
        <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
      </NuxtLink>
    </div>

    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('note.getNotesError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NoteList v-else-if="notes?.length" :notes="notes" :display-type="isUser" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noNotes') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'notes' });
const props = defineProps<{
  noteType?: Exclude<NoteType, 'Template'>;
  userEmail?: string;
  user?: User | null;
}>();

const { t } = useI18n();
const {
  data: notes,
  pending,
  error,
  refresh,
} = useGetNotes({
  type: props.noteType,
  user: props.userEmail,
});

const isUser = computed(() => Boolean(props.userEmail));
const noteTitles = computed(() => ({
  [NOTE_TYPE.goal]: t('common.goals'),
  [NOTE_TYPE.meeting]: t('common.meetings'),
  [NOTE_TYPE.message]: t('common.messageToOthers'),
  [NOTE_TYPE.personal]: t('common.personalNotes'),
  [NOTE_TYPE.proposal]: t('common.proposal'),
  [NOTE_TYPE.task]: t('common.tasks'),
}));
const noteTitle = computed(() =>
  props.noteType
    ? noteTitles.value[props.noteType]
    : props.user
      ? t('user.userNotes', { name: props.user.name })
      : t('common.notes'),
);

useHead({
  title: noteTitle,
});
</script>