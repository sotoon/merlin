<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="isDeleteLoading" class="text-primary" />

    <PInlineConfirm
      v-else
      :confirm-button-text="t('common.delete')"
      :message="t('note.confirmDeleteNote')"
      @confirm="handleDelete"
    >
      <PIconButton
        :color="buttonColor"
        :icon="PeyTrashIcon"
        :variant="buttonVariant"
        @click.prevent
      />
    </PInlineConfirm>
  </div>
</template>

<script lang="ts" setup>
import { PIconButton, PInlineConfirm, PLoading } from '@pey/core';
import { PeyTrashIcon } from '@pey/icons';

type ButtonColor = 'primary' | 'danger';
type ButtonVariant = 'fill' | 'ghost';

const props = withDefaults(
  defineProps<{
    noteId: string;
    buttonColor?: ButtonColor;
    buttonVariant?: ButtonVariant;
  }>(),
  {
    buttonColor: 'danger',
    buttonVariant: 'fill',
  },
);
const emit = defineEmits<{ success: [] }>();

const { t } = useI18n();
const { mutate: deleteNote, isPending: isDeleteLoading } = useDeleteNote(
  props.noteId,
);

const handleDelete = () => {
  deleteNote(undefined, {
    onSuccess: () => {
      emit('success');
    },
  });
};
</script>
