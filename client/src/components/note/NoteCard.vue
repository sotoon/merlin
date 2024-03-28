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
        <div class="flex gap-2">
          <PText class="text-gray-50" variant="caption2">
            {{ note.date }}
          </PText>

          <PText v-if="displayWriter" class="text-gray-50" variant="caption2">
            {{ `${t('note.writer')}: ${note.owner_name}` }}
          </PText>

          <PText
            v-if="displayType && note.type !== 'Template'"
            class="text-gray-50"
            variant="caption2"
          >
            {{ `${t('note.type')}: ${noteTypeLabel[note.type]}` }}
          </PText>
        </div>

        <template v-if="note.access_level.can_edit">
          <PLoading v-if="isDeleteLoading" class="m-1.5 text-primary" />

          <PIconButton
            v-else
            :icon="PeyTrashIcon"
            variant="ghost"
            @click.prevent="deleteNote"
          />
        </template>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PIconButton, PLoading, PText } from '@pey/core';
import { PeyTrashIcon } from '@pey/icons';

const props = defineProps<{
  note: Note;
  displayWriter?: boolean;
  displayType?: boolean;
}>();

const { t } = useI18n();
const { execute: deleteNote, pending: isDeleteLoading } = useDeleteNote({
  id: props.note.uuid,
});

const noteTypeLabel = computed(() => ({
  [NOTE_TYPE.goal]: t('noteType.goal'),
  [NOTE_TYPE.meeting]: t('noteType.meeting'),
  [NOTE_TYPE.message]: t('noteType.message'),
  [NOTE_TYPE.personal]: t('noteType.personal'),
  [NOTE_TYPE.proposal]: t('noteType.proposal'),
  [NOTE_TYPE.task]: t('noteType.task'),
}));
</script>
