<template>
  <PCard header-variant="primary" :title="feedback.owner_name">
    <article>
      <EditorContent :content="feedback.content" />
    </article>

    <template v-if="feedback.owner === profile?.email" #toolbar>
      <div class="flex items-center justify-end gap-3 sm:ms-4">
        <div class="flex h-8 w-8 items-center justify-center">
          <PLoading v-if="isDeleteLoading" class="text-primary" />

          <PInlineConfirm
            v-else
            :confirm-button-text="t('common.delete')"
            :message="t('note.confirmDeleteMessage')"
            @confirm="deleteNoteFeedback"
          >
            <PIconButton color="danger" :icon="PeyTrashIcon" variant="ghost" />
          </PInlineConfirm>
        </div>

        <PIconButton
          :icon="PeyEditIcon"
          variant="ghost"
          @click="emit('edit')"
        />
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PIconButton, PInlineConfirm, PLoading } from '@pey/core';
import { PeyEditIcon, PeyTrashIcon } from '@pey/icons';

const props = defineProps<{ note: Note; feedback: NoteFeedback }>();
const emit = defineEmits<{ edit: [] }>();

const { t } = useI18n();
const { data: profile } = useGetProfile();
const { execute: deleteNoteFeedback, pending: isDeleteLoading } =
  useDeleteNoteFeedback({
    noteId: props.note.uuid,
    feedbackId: props.feedback.uuid,
  });
</script>
