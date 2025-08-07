<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="text-h1 text-primary" :class="NOTE_TYPE_ICON[noteType]" />

      <PHeading level="h1" responsive>
        {{ t('note.createNewX', [noteTypeLabel]) }}
      </PHeading>
    </div>

    <NoteForm
      :note-type="noteType"
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'note-create' });
const props = defineProps<{ noteType: NoteType }>();

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const { mutate: createNote, isPending } = useCreateNote();

const noteTypeLabels = computed(() => getNoteTypeLabels(t));
const proposalTypeLabels = computed(() => getProposalTypeLabels(t));

const handleSubmit = (
  values: NoteFormValues,
  ctx: SubmissionContext<NoteFormValues>,
) => {
  const date = values.date || new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote(
    {
      ...values,
      date: dateString,
      type: props.noteType as Schema<'TypeEnum'>,
    },
    {
      onSuccess: (newNote) => {
        navigateTo({ name: 'note', params: { id: newNote.uuid } });
        ctx.resetForm();
      },
    },
  );
};

const handleCancel = () => {
  router.back();
};

const noteTypeLabel = computed(() =>
  props.noteType === NOTE_TYPE.proposal
    ? proposalTypeLabels.value[route.query.proposal_type as ProposalType]
    : noteTypeLabels.value[props.noteType],
);
</script>
