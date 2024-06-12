<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="text-h1 text-primary" :class="pageIcon" />

        <PHeading level="h1" responsive>
          {{ pageTitle }}
        </PHeading>
      </div>

      <NuxtLink :to="{ name: 'feedback-create' }">
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

    <template v-else>
      <NoteListControls v-if="notes?.length">
        <template #sort>
          <NoteListSortControl />
        </template>

        <template #filter>
          <NoteListPeriodFilter :notes="notes" />
        </template>
      </NoteListControls>

      <NoteList v-if="sortedNotes.length" :notes="sortedNotes" />

      <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
        {{ t('note.noNotes') }}
      </PText>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ type: FeedbackType }>();
definePageMeta({ name: 'feedbacks' });

const { t } = useI18n();
const {
  data: notes,
  pending,
  error,
  refresh,
} = useGetNotes(
  { type: NOTE_TYPE.message },
  {
    transform: (notes) =>
      notes.filter((note) => note.feedbackType === props.type),
  },
);
const filteredNotes = useFilterNotes(() => notes.value || []);
const sortedNotes = useSortNotes(filteredNotes);

const pageTitle = computed(() =>
  props.type === FEEDBACK_TYPE.Send
    ? t('common.sendFeedback')
    : t('common.requestFeedback'),
);
const pageIcon = computed(() =>
  props.type === FEEDBACK_TYPE.Send
    ? 'i-mdi-feedback'
    : 'i-mdi-comment-question',
);

useHead({
  title: pageTitle,
});
</script>
