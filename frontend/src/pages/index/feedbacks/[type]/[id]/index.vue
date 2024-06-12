<template>
  <NoteDetail :note="note">
    <template v-if="note.access_level.can_edit" #actions>
      <PIconButton
        class="shrink-0"
        :icon="PeyEditIcon"
        type="button"
        @click="navigateTo({ name: 'feedback-edit' })"
      />

      <NoteDeleteButton
        :note-id="note.uuid"
        @success="navigateTo({ name: 'feedbacks' })"
      />
    </template>
  </NoteDetail>
</template>

<script lang="ts" setup>
import { PIconButton } from '@pey/core';
import { PeyEditIcon } from '@pey/icons';

definePageMeta({ name: 'feedback' });
defineProps<{ note: Note }>();
</script>
