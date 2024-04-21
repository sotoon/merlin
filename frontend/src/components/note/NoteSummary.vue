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

    <article class="mt-4 py-4">
      <EditorContent :content="summaries[0].content" />

      <PBox>
        <PropertyTable>
          <PropertyTableRow
            :label="t('note.performanceLabel')"
            :value="summaries[0].performance_label"
          />

          <PropertyTableRow
            :label="t('note.performanceBonus')"
            :value="
              (summaries[0].bonus / 100).toLocaleString('fa-IR', {
                style: 'percent',
              })
            "
          />

          <PropertyTableRow
            :label="t('note.ladderChange')"
            :value="summaries[0].ladder_change"
          />

          <PropertyTableRow
            :label="t('note.salaryChange')"
            :value="summaries[0].salary_change.toLocaleString('fa-IR')"
          />

          <PropertyTableRow
            :label="t('note.committeeDate')"
            :value="
              summaries[0].committee_date
                ? new Date(summaries[0].committee_date).toLocaleDateString(
                    'fa-IR',
                  )
                : '-'
            "
          />
        </PropertyTable>
      </PBox>
    </article>
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
import {
  PBox,
  PButton,
  PHeading,
  PIconButton,
  PLoading,
  PText,
} from '@pey/core';
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
