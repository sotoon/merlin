<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="readStatusPending" class="text-primary" />

    <button
      v-else
      class="rounded p-1 text-h3 transition-colors hover:bg-primary-10"
      @click="toggleReadStatus"
    >
      <i v-if="note.read_status" class="i-mdi-email-open block text-gray-30" />
      <i v-else class="i-mdi-email block text-primary" />
    </button>
  </div>
</template>

<script lang="ts" setup>
import { PLoading } from '@pey/core';

const props = defineProps<{ note: Note }>();

const { mutate: updateReadStatus, isPending: readStatusPending } =
  useUpdateNoteReadStatus();

const toggleReadStatus = () => {
  updateReadStatus(props.note.uuid, !props.note.read_status);
};
</script>
