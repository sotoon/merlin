<template>
  <PLoading v-if="isPending" class="text-primary" />

  <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
    <PText as="p" class="text-center text-danger" responsive>
      {{ t('note.getSummaryError') }}
    </PText>

    <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
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

      <div
        v-if="
          summaries[0]?.submit_status === NOTE_SUMMARY_SUBMIT_STATUS.initial
        "
        class="flex items-center gap-2"
      >
        <template v-if="note.access_level.can_write_summary">
          <PTooltip
            :model-value="finalSubmitHintVisibility"
            placement="top-end"
          >
            <template #content>
              <PText as="p" class="max-w-xs">
                {{ t('note.finalSubmitSummaryHint') }}
              </PText>
            </template>

            <div ref="finalSubmitButton">
              <PInlineConfirm
                v-if="note.type === NOTE_TYPE.proposal"
                confirm-button-color="primary"
                :confirm-button-text="t('note.finalSubmit')"
                @confirm="finalizeSummarySubmission"
              >
                <template #text>
                  <PText as="p" class="text-gray-80">
                    {{ t('note.confirmSubmitSummary') }}
                  </PText>

                  <PText as="p" class="mt-2 text-gray-80">
                    {{ t('note.confirmSubmitSummaryMessage') }}
                  </PText>
                </template>

                <PButton
                  color="primary"
                  :icon-start="PeyCircleTickOutlineIcon"
                  :loading="updatingSummary"
                  size="small"
                  type="button"
                  variant="fill"
                >
                  {{ t('note.finalSubmit') }}
                </PButton>
              </PInlineConfirm>
            </div>
          </PTooltip>

          <PIconButton
            class="shrink-0"
            :icon="PeyEditIcon"
            type="button"
            @click="navigateTo({ name: 'note-summary' })"
          />
        </template>
      </div>

      <PChip
        v-else
        class="whitespace-nowrap"
        color="success"
        :icon="PeyCircleTickOutlineIcon"
        :label="t('note.submitStatus.final')"
        size="small"
      />
    </div>

    <article class="mt-4 py-4">
      <EditorContent :content="summaries[0].content" />

      <PBox v-if="note.type === NOTE_TYPE.proposal">
        <PropertyTable>
          <PropertyTableRow
            :label="t('note.performanceLabel')"
            :value="summaries[0].performance_label"
          />

          <PropertyTableRow
            :label="t('note.performanceBonus')"
            :value="
              summaries[0].bonus
                ? (summaries[0].bonus / 100).toLocaleString('fa-IR', {
                    style: 'percent',
                  })
                : '-'
            "
          />

          <PropertyTableRow
            :label="t('note.ladderChange')"
            :value="summaries[0].ladder_change"
          />

          <PropertyTableRow
            :label="t('note.salaryChange')"
            :value="
              summaries[0].salary_change
                ? summaries[0].salary_change.toLocaleString('fa-IR')
                : '-'
            "
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
  PChip,
  PHeading,
  PIconButton,
  PInlineConfirm,
  PLoading,
  PText,
  PTooltip,
} from '@pey/core';
import {
  PeyCircleTickOutlineIcon,
  PeyEditIcon,
  PeyPlusIcon,
  PeyRetryIcon,
} from '@pey/icons';
import { useQueryClient } from '@tanstack/vue-query';

const props = defineProps<{ note: Note }>();

let finalSubmitHintTimeout: NodeJS.Timeout | null = null;
const finalSubmitHintVisibility = ref(false);
const finalSubmitButton = ref<HTMLElement | null>(null);

const queryClient = useQueryClient();
const { t } = useI18n();
const {
  data: summaries,
  isPending,
  error,
  refetch,
} = useGetNoteSummaries({
  noteId: props.note.uuid,
});
const { mutate: updateSummary, isPending: updatingSummary } =
  useCreateNoteSummary(props.note.uuid);

const finalizeSummarySubmission = () => {
  if (!summaries.value?.length) return;

  updateSummary(
    {
      ...summaries.value[0],
      submit_status: NOTE_SUMMARY_SUBMIT_STATUS.final,
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['note', props.note.uuid] });
      },
    },
  );
};

watch(
  finalSubmitButton,
  () => {
    if (props.note.type === NOTE_TYPE.proposal && finalSubmitButton.value) {
      const observer = new IntersectionObserver(
        (entries) => {
          if (entries[0]?.isIntersecting) {
            finalSubmitHintTimeout = setTimeout(() => {
              finalSubmitHintVisibility.value = true;

              finalSubmitHintTimeout = setTimeout(() => {
                finalSubmitHintVisibility.value = false;
              }, 5000);
            }, 1000);

            observer.disconnect();
          }
        },
        {
          root: null,
          rootMargin: '-100px',
        },
      );

      observer.observe(finalSubmitButton.value);
    }
  },
  { once: true },
);

onBeforeUnmount(() => {
  finalSubmitHintTimeout && clearTimeout(finalSubmitHintTimeout);
});
</script>
