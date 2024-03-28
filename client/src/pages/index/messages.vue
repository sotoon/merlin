<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <PHeading level="h1" responsive>
        {{ t('common.messages') }}
      </PHeading>
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

    <NoteList v-else-if="notes?.length" :notes="notes" is-messages />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noNotes') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const { t } = useI18n();
useHead({ title: t('common.messages') });
const {
  data: notes,
  pending,
  error,
  refresh,
} = useGetNotes({
  retrieveMentions: true,
});
</script>
