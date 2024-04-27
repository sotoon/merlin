<template>
  <PCard
    :footer-border="false"
    :header-border="false"
    header-variant="primary-dark"
    :title="note.title"
  >
    <EditorContentPreview class="text-gray-80" :content="note.content" />

    <template v-if="displayType" #icon>
      <PChip :label="noteTypeLabel[note.type]" size="small" />
    </template>

    <template v-if="note.access_level.can_edit || displayReadStatus" #toolbar>
      <div class="ms-4 hidden sm:block">
        <div
          v-if="note.access_level.can_edit"
          class="flex h-8 w-8 items-center justify-center"
          @click.prevent
        >
          <PLoading v-if="isDeleteLoading" class="text-white" />

          <PInlineConfirm
            v-else
            :message="t('common.confirmDeleteX', [note.title])"
            @confirm="deleteNote"
          >
            <PIconButton :icon="PeyTrashIcon" variant="fill" @click.prevent />
          </PInlineConfirm>
        </div>

        <NoteReadToggle v-else-if="displayReadStatus" :note="note" />
      </div>
    </template>

    <template #footer>
      <div class="flex grow items-end justify-between gap-2 overflow-hidden">
        <div
          class="flex flex-col gap-2 overflow-hidden text-gray-50 sm:flex-row sm:items-center"
        >
          <PTooltip>
            <PText class="text-nowrap" variant="caption2">
              {{ formatTimeAgo(new Date(note.date_updated), 'fa-IR') }}
            </PText>

            <template #content>
              <PText variant="caption2">
                {{ t('note.lastEdit') }}:
                <PText dir="ltr" variant="caption1">
                  {{ new Date(note.date_updated).toLocaleString('fa-IR') }}
                </PText>
              </PText>
            </template>
          </PTooltip>

          <PText v-if="displayWriter" class="truncate" variant="caption2">
            {{ note.owner_name }}
          </PText>
        </div>

        <div v-if="note.type !== NOTE_TYPE.template">
          <PText class="text-nowrap text-gray-50" dir="ltr" variant="caption2">
            {{
              note.type === NOTE_TYPE.meeting
                ? new Date(note.date).toLocaleDateString('fa-IR')
                : `${note.year.toLocaleString('fa-IR', { useGrouping: false })} - ${(note.period + 1).toLocaleString('fa-IR')}`
            }}
          </PText>
        </div>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import {
  PCard,
  PChip,
  PIconButton,
  PInlineConfirm,
  PLoading,
  PText,
  PTooltip,
} from '@pey/core';
import { PeyTrashIcon } from '@pey/icons';

const props = defineProps<{
  note: Note;
  displayWriter?: boolean;
  displayType?: boolean;
  displayReadStatus?: boolean;
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
  [NOTE_TYPE.template]: t('noteType.template'),
}));
</script>
