<template>
  <PLoading v-if="pending" class="text-primary" />

  <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
    <PText as="p" class="text-center text-danger" responsive>
      {{ t('note.getSummaryError') }}
    </PText>

    <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
      {{ t('common.retry') }}
    </PButton>
  </div>

  <template v-else-if="summaries?.length">
    <div
      class="flex items-center justify-between gap-4 border-b border-gray-10 pb-4"
    >
      <PHeading :lvl="3" responsive>
        {{ t('note.summary') }}
      </PHeading>

      <PIconButton
        v-if="note.access_level.can_write_summary"
        class="shrink-0"
        :icon="PeyEditIcon"
        type="button"
        @click="navigateTo({ name: 'note-summary' })"
      />
    </div>

    <div
      v-dompurify-html="summaries[0].content"
      class="prose py-4"
      dir="auto"
    />
  </template>

  <PButton
    v-else-if="note.access_level.can_write_summary"
    :icon-start="PeyPlusIcon"
    variant="ghost"
    @click="navigateTo({ name: 'note-summary' })"
  >
    {{ t('note.writeSummary') }}
  </PButton>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyEditIcon, PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const {
  data: summaries,
  pending,
  error,
  refresh,
} = useGetNoteSummaries({
  noteId: props.note.uuid,
});
</script>
