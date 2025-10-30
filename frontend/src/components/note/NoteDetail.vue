<template>
  <div class="px-2 sm:px-4">
    <div class="flex items-start justify-between gap-8">
      <div>
        <i
          class="mb-3 me-4 inline-block align-middle text-h1 text-primary"
          :class="noteTypeIcon"
        />

        <PText responsive variant="h1" weight="bold">
          {{ note.title }}
        </PText>
      </div>

      <div class="mt-2 flex flex-col items-end gap-4">
        <div v-if="note.access_level.can_edit" class="flex items-center gap-4">
          <PIconButton
            class="shrink-0"
            :icon="PeyEditIcon"
            type="button"
            @click="navigateTo({ name: 'note-edit' })"
          />

          <NoteDeleteButton
            :note-id="note.uuid"
            @success="navigateTo({ name: 'notes' })"
          />
        </div>
      </div>
    </div>

    <div
      v-if="note.type === NOTE_TYPE.proposal"
      class="mt-6 flex flex-wrap items-center justify-between gap-4"
    >
      <template v-if="note.submit_status === NOTE_SUBMIT_STATUS.initial">
        <PChip
          class="whitespace-nowrap"
          color="warning"
          :icon="PeyCreateIcon"
          :label="t('note.submitStatus.initial')"
        />

        <PTooltip
          v-if="note.access_level.can_edit"
          :model-value="finalSubmitHintVisibility"
          placement="right"
        >
          <template #content>
            <PText as="p" class="max-w-sm">
              {{ t('note.finalSubmitProposalHint') }}
            </PText>
          </template>

          <div>
            <PInlineConfirm
              confirm-button-color="primary"
              :confirm-button-text="t('note.finalSubmit')"
              @confirm="finalizeNoteSubmission"
            >
              <template #text>
                <PText as="p" class="text-gray-80">
                  {{ t('note.confirmSubmitProposal') }}
                </PText>

                <PText as="p" class="mt-2 text-gray-80">
                  {{ t('note.confirmSubmitProposalMessage') }}
                </PText>
              </template>

              <PButton
                type="button"
                class="whitespace-nowrap"
                color="primary"
                :icon-start="PeyCircleTickOutlineIcon"
                :loading="updatingNote"
                variant="fill"
              >
                {{ t('note.finalSubmit') }}
              </PButton>
            </PInlineConfirm>
          </div>
        </PTooltip>
      </template>

      <PChip
        v-else-if="note.submit_status === NOTE_SUBMIT_STATUS.final"
        class="whitespace-nowrap"
        color="secondary"
        :icon="PeyClockIcon"
        :label="t('note.submitStatus.pending')"
      />

      <PChip
        v-else
        class="whitespace-nowrap"
        color="success"
        :icon="PeyCircleTickOutlineIcon"
        :label="t('note.submitStatus.reviewed')"
      />
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.lastEdit') }}:
        <PTooltip>
          <PText class="text-gray-70" variant="caption1">
            {{ formatTimeAgo(new Date(note.date_updated), 'fa-IR') }}
          </PText>

          <template #content>
            <PText dir="ltr" variant="caption1">
              {{ new Date(note.date_updated).toLocaleString('fa-IR') }}
            </PText>
          </template>
        </PTooltip>
      </PText>

      <PText
        v-if="
          !note.access_level.can_edit && profile && note.owner !== profile.email
        "
        as="p"
        class="text-gray-50"
        variant="caption1"
      >
        {{ t('note.writer') }}:
        <NuxtLink
          class="text-primary hover:underline"
          :to="{
            name: 'user-detail',
            params: { id: note.owner_uuid },
          }"
        >
          {{ note.owner_name }}
        </NuxtLink>
      </PText>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{
          note.type === NOTE_TYPE.meeting
            ? t('note.meetingDate')
            : t('common.date')
        }}:
        <PText class="text-gray-70" variant="caption1">
          {{ new Date(note.date).toLocaleDateString('fa-IR') }}
        </PText>
      </PText>

      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.period') }}:
        <PText class="text-gray-70" variant="caption1">
          {{ EVALUATION_PERIODS[note.period] || '' }}
          {{ note.year.toLocaleString('fa-IR', { useGrouping: false }) }}
        </PText>
      </PText>
    </div>

    <article class="mt-4 py-4">
      <EditorContent :content="note.content" />
    </article>

    <div v-if="mentionedUsers?.length" class="mt-4">
      <PHeading :lvl="4" responsive>
        {{ t('note.mentionedUsers') }}
      </PHeading>

      <div class="mt-4 flex flex-wrap gap-2">
        <PChip
          v-for="user in mentionedUsers"
          :key="user.uuid"
          :label="user.name || user.email"
          size="small"
        />
      </div>
    </div>

    <div v-if="linkedNotes?.length" class="mt-8">
      <PHeading :lvl="4" responsive>
        {{ t('note.relatedNotes') }}
      </PHeading>

      <div class="mt-4 flex flex-wrap gap-2">
        <NuxtLink
          v-for="linkedNote in linkedNotes"
          :key="linkedNote.uuid"
          class="*:cursor-pointer"
          :to="linkedNote.to"
        >
          <PChip
            color="primary"
            :icon="PeyLinkIcon"
            :label="linkedNote.title"
            size="small"
          />
        </NuxtLink>
      </div>
    </div>

    <div
      v-if="
        NOTES_WITH_SUMMARY.includes(note.type) &&
        note.access_level.can_view_summary
      "
      class="mt-8"
    >
      <NoteSummary :note="note" />
    </div>

    <div class="mt-8">
      <NoteComments :note="note" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  PButton,
  PChip,
  PHeading,
  PIconButton,
  PInlineConfirm,
  PText,
  PTooltip,
} from '@pey/core';
import {
  PeyCircleTickOutlineIcon,
  PeyClockIcon,
  PeyCreateIcon,
  PeyEditIcon,
  PeyLinkIcon,
} from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const { data: profile } = useGetProfile();
const { data: users } = useGetUsers();
const { mutate: updateNote, isPending: updatingNote } = useUpdateNote(
  props.note.uuid,
);

let finalSubmitHintTimeout: NodeJS.Timeout | null = null;
const finalSubmitHintVisibility = ref(false);

const mentionedUsers = computed(() =>
  users.value?.filter(({ email }) =>
    props.note.mentioned_users.includes(email),
  ),
);

onMounted(() => {
  if (props.note.type === NOTE_TYPE.proposal) {
    finalSubmitHintTimeout = setTimeout(() => {
      finalSubmitHintVisibility.value = true;

      finalSubmitHintTimeout = setTimeout(() => {
        finalSubmitHintVisibility.value = false;
      }, 5000);
    }, 1000);
  }
});

onBeforeUnmount(() => {
  finalSubmitHintTimeout && clearTimeout(finalSubmitHintTimeout);
});

function finalizeNoteSubmission() {
  updateNote({
    submit_status: NOTE_SUBMIT_STATUS.final,
  });
}

function getNoteRoute(note: Schema<'LinkedNote'>) {
  switch (note.type) {
    case NOTE_TYPE.template:
      return {
        name: 'template',
        params: { id: note.uuid },
      };
    case NOTE_TYPE.oneOnOne:
      return {
        name: 'one-on-one-id',
        params: {
          userId: note.one_on_one_member,
          id: note.one_on_one_id,
        },
      };
    case NOTE_TYPE.feedbackRequest:
      return {
        name: 'feedback-detail',
        params: { requestId: note.feedback_request_uuid },
      };
    case NOTE_TYPE.feedback:
      return {
        name: 'adhoc-feedback-detail',
        params: { id: note.feedback_uuid },
      };
    default:
      return {
        name: 'note',
        params: {
          type: NOTE_TYPE_ROUTE_PARAM[
            note.type as keyof typeof NOTE_TYPE_ROUTE_PARAM
          ],
          id: note.uuid,
        },
      };
  }
}

const linkedNotes = computed(() => {
  return props.note.linked_notes.map((note) => ({
    ...note,
    to: getNoteRoute(note),
  }));
});

const noteTypeIcon = computed(() => {
  return props.note.type === NOTE_TYPE.proposal
    ? PROPOSAL_TYPE_ICON[props.note.proposal_type as ProposalType]
    : props.note.type
      ? NOTE_TYPE_ICON[props.note.type]
      : 'i-mdi-note-text';
});
</script>
