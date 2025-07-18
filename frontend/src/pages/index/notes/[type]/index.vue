<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i
          class="text-h1 text-primary"
          :class="noteType ? NOTE_TYPE_ICON[noteType] : 'i-mdi-note-text'"
        />

        <PHeading level="h1" responsive>
          {{ noteTitle }}
        </PHeading>
      </div>

      <NuxtLink
        v-if="!isUser && noteType !== NOTE_TYPE.message"
        :to="{ name: 'note-create' }"
      >
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
      <template v-if="notes?.length">
        <NoteTypeFilter v-if="!noteType" :notes />

        <NoteListControls>
          <NoteSearchFilter />

          <template #sort>
            <NoteSortControl :sort-by-date="noteType === NOTE_TYPE.meeting" />
          </template>

          <template #filter>
            <NotePeriodFilter :notes />
          </template>
        </NoteListControls>
      </template>

      <PAlert
        v-if="noteType === NOTE_TYPE.message"
        title="این قسمت به زودی حذف خواهد شد"
        content="اگر اطلاعات مهمی در این قسمت دارید، لطفا آن‌ها را بردارید. از این پس می‌توانید از قسمت «درخواست فیدبک» یا «فیدبک مستقیم» استفاده کنید."
        variant="danger"
      />

      <NoteList
        v-if="sortedNotes.length"
        :notes="sortedNotes"
        :display-type="isUser"
        :display-read-status="isUser"
      />

      <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
        {{ t('note.noNotes') }}
      </PText>
    </template>
  </div>
</template>

<script lang="ts" setup>
import {
  PButton,
  PHeading,
  PIconButton,
  PLoading,
  PText,
  PAlert,
} from '@pey/core';
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
// TODO: filter out templates in the backend
const filteredNotes = useFilterNotes(
  () => notes.value?.filter((note) => note.type !== NOTE_TYPE.template) || [],
);
const sortedNotes = useSortNotes(filteredNotes);

const isUser = computed(() => Boolean(props.userEmail));
const noteTitles = computed(() => ({
  [NOTE_TYPE.goal]: t('common.goals'),
  [NOTE_TYPE.meeting]: t('common.meetings'),
  [NOTE_TYPE.oneOnOne]: t('common.oneOnOne'),
  [NOTE_TYPE.message]: t('common.messageToOthers'),
  [NOTE_TYPE.proposal]: t('common.proposal'),
  [NOTE_TYPE.forms]: t('common.forms'),
  [NOTE_TYPE.feedbackRequest]: t('common.feedbackRequest'),
  [NOTE_TYPE.feedback]: t('common.feedback'),
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
