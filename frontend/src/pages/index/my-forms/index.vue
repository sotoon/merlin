<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-form text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('common.myForms') }}
        </PHeading>
      </div>

      <NuxtLink :to="{ name: 'form-assign' }">
        <PButton
          color="primary"
          :icon-start="PeyPlusIcon"
          variant="fill"
          tabindex="-1"
        >
          {{ t('form.assignForm') }}
        </PButton>
      </NuxtLink>
    </div>

    <div v-if="pending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        <!-- // TODO: fix error message -->
        {{ t('note.getNotesError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <template v-else>
      <!-- <template v-if="forms?.length">
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
      </template> -->

      <!-- // TODO: separate completed and incomplete forms -->
      <FormList v-if="forms?.active_forms.length" :forms="forms.active_forms" />

      <!-- <NoteList
        v-if="sortedNotes.length"
        :notes="sortedNotes"
        :display-type="isUser"
        :display-read-status="isUser"
      /> -->

      <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
        {{ t('note.noNotes') }}
      </PText>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PLoading, PText } from '@pey/core';
import { PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'my-forms' });

const { t } = useI18n();
const { data: forms, pending, error, refresh } = useGetForms();

useHead({
  title: t('common.myForms'),
});
</script>
