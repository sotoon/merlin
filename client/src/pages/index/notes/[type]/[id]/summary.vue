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
      :is-submitting="pending"
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
const { data: summaries, pending: getSummariesPending } = useGetNoteSummaries({
  noteId: props.note.uuid,
});
const { execute: createNoteSummary, pending } = useCreateNoteSummary({
  noteId: props.note.uuid,
});

const handleSubmit = (
  values: NoteSummaryFormValues,
  ctx: SubmissionContext<NoteSummaryFormValues>,
) => {
  createNoteSummary({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      navigateTo({ name: 'note' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};

onMounted(() => {
  if (!props.note.access_level.can_write_summary) {
    navigateTo({ name: 'note', replace: true });
  }
});
</script>
