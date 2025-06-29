<template>
  <PLoading v-if="pending" class="text-primary" />

  <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
    <PText as="p" class="text-center text-danger" responsive>
      {{ t('note.getCommentsError') }}
    </PText>

    <PButton color="gray" :icon-start="PeyRetryIcon" @click="refresh">
      {{ t('common.retry') }}
    </PButton>
  </div>

  <template v-else-if="comments?.length">
    <div
      class="flex items-center justify-between gap-4 border-b border-gray-10 pb-4"
    >
      <PHeading :lvl="3" responsive>
        {{ t('note.comments') }}
      </PHeading>

      <PIconButton
        v-if="note.access_level.can_write_feedback"
        class="shrink-0"
        :icon="userHasWrittenComment ? PeyEditIcon : PeyPlusIcon"
        type="button"
        @click="
          navigateTo({
            name: 'note-comment',
            query: {
              owner: userHasWrittenComment ? profile?.email : undefined,
            },
          })
        "
      />
    </div>

    <div class="p-4">
      <NoteCommentList :comments="comments" />
    </div>
  </template>

  <PButton
    v-else-if="note.access_level.can_write_feedback"
    :icon-start="PeyPlusIcon"
    variant="ghost"
    @click="navigateTo({ name: 'note-comment' })"
  >
    {{ t('note.writeComment') }}
  </PButton>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyEditIcon, PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

const props = defineProps<{ note: Note }>();

const { t } = useI18n();
const {
  data: comments,
  pending,
  error,
  refresh,
} = useGetNoteComments({
  noteId: props.note.uuid,
});
const { data: profile } = useGetProfile();

const userHasWrittenComment = computed(() =>
  comments.value?.some((comment) => comment.owner === profile.value?.email),
);
</script>
