<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="isDeleteLoading" class="text-white" />

    <PInlineConfirm
      v-else
      :confirm-button-text="t('common.delete')"
      :message="t('note.confirmDeleteNote')"
      @confirm="handleDelete"
    >
      <PIconButton
        :color="buttonColor"
        :icon="PeyTrashIcon"
        variant="fill"
        @click.prevent
      />
    </PInlineConfirm>
  </div>
</template>

<script lang="ts" setup>
import { PIconButton, PInlineConfirm, PLoading } from '@pey/core';
import { PeyTrashIcon } from '@pey/icons';

type ButtonColor = 'primary' | 'danger';

const props = withDefaults(
  defineProps<{ noteId: string; buttonColor?: ButtonColor }>(),
  {
    buttonColor: 'primary',
  },
);
const emit = defineEmits<{ success: [] }>();

const { t } = useI18n();
const { execute: deleteNote, pending: isDeleteLoading } = useDeleteNote({
  id: props.noteId,
});

const handleDelete = () => {
  deleteNote({
    onSuccess: () => {
      emit('success');
    },
  });
};
</script>
