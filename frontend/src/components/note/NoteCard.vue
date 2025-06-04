<template>
  <PCard
    class="transition-shadow duration-300 hover:shadow-lg"
    header-border
    :title="note.title"
  >
    <EditorContentPreview class="text-gray-80" :content="note.content" />

    <template #title>
      <PText as="h3" class="truncate" weight="medium">
        {{ note.title }}
      </PText>
    </template>

    <template v-if="displayType" #icon>
      <div :title="noteTypeLabel[note.type]">
        <i class="block text-h3 text-gray" :class="NOTE_TYPE_ICON[note.type]" />
      </div>
    </template>

    <template
      v-if="
        note.access_level.can_edit || displayReadStatus || displaySubmitStatus
      "
      #toolbar
    >
      <div class="flex items-center justify-end gap-1 sm:ms-4" @click.prevent>
        <template v-if="displaySubmitStatus">
          <PChip
            v-if="note.submit_status === NOTE_SUBMIT_STATUS.initial"
            class="whitespace-nowrap"
            color="warning"
            :icon="PeyCreateIcon"
            :label="t('note.submitStatus.initial')"
            size="small"
          />

          <PChip
            v-else-if="note.submit_status === NOTE_SUBMIT_STATUS.final"
            class="whitespace-nowrap"
            color="secondary"
            :icon="PeyClockIcon"
            :label="t('note.submitStatus.pending')"
            size="small"
          />

          <PChip
            v-else
            class="whitespace-nowrap"
            color="success"
            :icon="PeyCircleTickOutlineIcon"
            :label="t('note.submitStatus.reviewed')"
            size="small"
          />
        </template>

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

        <div
          v-if="
            note.type !== NOTE_TYPE.template && note.type === NOTE_TYPE.meeting
          "
        >
          <PText class="text-nowrap text-gray-50" dir="ltr" variant="caption2">
            {{ new Date(note.date).toLocaleDateString('fa-IR') }}
          </PText>
        </div>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PChip, PText, PTooltip } from '@pey/core';
import {
  PeyCircleTickOutlineIcon,
  PeyClockIcon,
  PeyCreateIcon,
} from '@pey/icons';

const props = defineProps<{
  note: Note;
  displayWriter?: boolean;
  displayType?: boolean;
  displayReadStatus?: boolean;
}>();

const { t } = useI18n();

const noteTypeLabel = computed(() => getNoteTypeLabels(t));

const displaySubmitStatus = computed(
  () => props.note.type === NOTE_TYPE.proposal,
);
</script>
