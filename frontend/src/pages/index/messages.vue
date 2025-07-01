<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-message-text text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('common.messages') }}
        </PHeading>
      </div>
    </div>

    <div
      v-if="!notes && isPending"
      class="flex items-center justify-center py-8"
    >
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="isError" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('note.getMessagesError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <template v-else>
      <template v-if="notes?.length">
        <NoteTypeFilter :notes />

        <NoteListControls v-if="notes?.length">
          <NoteSearchFilter />

          <template #sort>
            <NoteSortControl :sort-by-date="typeFilter === NOTE_TYPE.meeting" />
          </template>

          <template #filter>
            <NoteWriterFilter :notes />
            <NoteTeamFilter v-if="isTeamLeader" />
            <NoteReadStatusFilter />
          </template>
        </NoteListControls>
      </template>

      <NoteList
        v-if="sortedNotes.length"
        :notes="sortedNotes"
        display-writer
        display-type
        display-read-status
      />

      <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
        {{ t('note.noMessages') }}
      </PText>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import { useRouteQuery } from '@vueuse/router';

definePageMeta({ name: 'messages' });

const { t } = useI18n();
useHead({ title: t('common.messages') });
const {
  data: notes,
  isPending,
  isError,
  refetch,
} = useGetNotes({
  retrieveMentions: true,
});
const isTeamLeader = useIsTeamLeader();

// TODO: filter out templates in the backend
const notesWithoutTemplates = computed(
  () => notes.value?.filter(({ type }) => type !== NOTE_TYPE.template) || [],
);
const filteredNotes = useFilterNotes(notesWithoutTemplates);
const sortedNotes = useSortNotes(filteredNotes);
const typeFilter = useRouteQuery<string>('type');
</script>
