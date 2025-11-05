<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="text-h1 text-primary" :class="noteTypeIcon" />

      <PHeading level="h1" responsive>
        {{ t('note.editX', [noteTypeLabel]) }}
      </PHeading>
    </div>

    <NoteForm
      :note="note"
      :note-type="note.type"
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>

<script lang="ts" setup>
import { PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-edit' });
const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { mutate: updateNote, isPending } = useUpdateNote(props.note.uuid);

const noteTypeLabels = computed(() => getNoteTypeLabels(t));
const proposalTypeLabels = computed(() => getProposalTypeLabels(t));

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  const dateString =
    values.date &&
    `${values.date.getFullYear()}-${values.date.getMonth() + 1}-${values.date.getDate()}`;

  updateNote(
    {
      ...values,
      linked_notes:
        values.linked_notes as unknown as Schema<'LinkedNoteRequest'>[],
      date: dateString,
    },
    {
      onSuccess: () => {
        navigateTo({ name: 'note' });
        ctx.resetForm();
      },
    },
  );
};

const handleCancel = () => {
  navigateTo({ name: 'note' });
};

const noteTypeLabel = computed(() =>
  props.note.type === NOTE_TYPE.proposal
    ? proposalTypeLabels.value[props.note.proposal_type as ProposalType]
    : noteTypeLabels.value[props.note.type],
);
const noteTypeIcon = computed(() => {
  return props.note.type === NOTE_TYPE.proposal
    ? PROPOSAL_TYPE_ICON[props.note.proposal_type as ProposalType]
    : props.note.type
      ? NOTE_TYPE_ICON[props.note.type]
      : 'i-mdi-note-text';
});
</script>
