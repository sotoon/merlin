<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.writeSummaryFor', { title: note.title }) }}
    </PHeading>

    <PLoading v-if="getSummariesPending" class="text-primary" :size="20" />

    <NoteSummaryForm
      v-else
      :note="note"
      :summary="summaries?.[0]"
      :show-committee-fields="note.type === NOTE_TYPE.proposal"
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>

<script lang="ts" setup>
import { PHeading, PLoading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-summary' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { data: summaries, isPending: getSummariesPending } = useGetNoteSummaries(
  { noteId: props.note.uuid },
);
const { mutate: createNoteSummary, isPending } = useCreateNoteSummary(
  props.note.uuid,
);

const handleSubmit = (
  values: Schema<'SummaryRequest'>,
  ctx: SubmissionContext<Schema<'SummaryRequest'>>,
) => {
  const committeeDateString =
    values.committee_date &&
    `${(values.committee_date as unknown as Date).getFullYear()}-${(values.committee_date as unknown as Date).getMonth() + 1}-${(values.committee_date as unknown as Date).getDate()}`;

  createNoteSummary(
    {
      ...values,
      committee_date: committeeDateString,
    },
    {
      onSuccess: () => {
        ctx.resetForm();
        navigateTo({ name: 'note', replace: true });
      },
    },
  );
};

const handleCancel = () => {
  navigateTo({ name: 'note', replace: true });
};

onMounted(() => {
  if (!props.note.access_level.can_write_summary) {
    navigateTo({ name: 'note', replace: true });
  }
});
</script>
