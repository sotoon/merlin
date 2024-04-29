<template>
  <PCard
    class="transition-shadow duration-300 hover:shadow-lg"
    header-border
    :title="note.title"
  >
    <EditorContentPreview class="text-gray-80" :content="note.content" />

    <template v-if="displayType" #icon>
      <div :title="noteTypeLabel[note.type]">
        <Icon class="text-gray" :name="NOTE_TYPE_ICON[note.type]" />
      </div>
    </template>

    <template v-if="note.access_level.can_edit || displayReadStatus" #toolbar>
      <div class="ms-4 hidden sm:block" @click.prevent>
        <NoteDeleteButton
          v-if="note.access_level.can_edit"
          button-color="danger"
          button-variant="ghost"
          :note-id="note.uuid"
        />

        <NoteReadToggle v-else-if="displayReadStatus" :note="note" />
      </div>
    </template>

    <template #footer>
      <div
        class="mt-2 flex grow items-end justify-between gap-2 overflow-hidden"
      >
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
import { PCard, PText, PTooltip } from '@pey/core';

defineProps<{
  note: Note;
  displayWriter?: boolean;
  displayType?: boolean;
  displayReadStatus?: boolean;
}>();

const { t } = useI18n();

const noteTypeLabel = computed(() => getNoteTypeLabels(t));
</script>
