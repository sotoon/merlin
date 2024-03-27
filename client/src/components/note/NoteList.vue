<template>
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

  <ul
    v-else-if="notes?.length"
    class="grid grid-cols-1 gap-2 py-4 lg:grid-cols-2 lg:gap-3"
  >
    <li v-for="note in notes" :key="note.uuid">
      <NuxtLink :to="`${path}/${note.uuid}`">
        <NoteCard :note="note" />
      </NuxtLink>
    </li>
  </ul>

  <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
    {{ t('note.noNotes') }}
  </PText>
</template>

<script lang="ts" setup>
import { PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ type?: NoteType }>();

const { t } = useI18n();
const { path } = useRoute();
const {
  data: notes,
  pending,
  error,
  refresh,
} = useGetNotes({ type: props.type });
</script>
