<template>
  <PCard
    :footer-border="false"
    :header-border="false"
    header-variant="primary-dark"
    :title="note.title"
  >
    <PText as="p" class="truncate text-gray-80">
      {{ extractTextFromHTML(note.content) }}
    </PText>

    <template #footer>
      <div class="flex grow items-center justify-between gap-2">
        <PText class="text-gray-50" variant="caption2">
          {{ note.date }}
        </PText>

        <PLoading v-if="isDeleteLoading" class="m-1.5 text-primary" />

        <PIconButton
          v-else
          :icon="PeyTrashIcon"
          variant="ghost"
          @click.prevent="deleteNote"
        />
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PIconButton, PLoading, PText } from '@pey/core';
import { PeyTrashIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { execute: deleteNote, pending: isDeleteLoading } = useDeleteNote({
  id: props.note.uuid,
});
</script>
