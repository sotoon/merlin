<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="readStatusPending" class="text-primary" />

    <button
      v-else
      class="rounded p-1 transition-colors hover:bg-primary-10"
      @click="toggleReadStatus"
    >
      <Icon v-if="note.read_status" class="text-gray" name="mdi:email-open" />
      <Icon v-else class="text-primary" name="mdi:email" />
    </button>
  </div>
</template>

<script lang="ts" setup>
import { PLoading } from '@pey/core';

const props = defineProps<{ note: Note }>();

const { execute: updateReadStatus, pending: readStatusPending } =
  useUpdateNoteReadStatus({
    id: props.note.uuid,
  });

const toggleReadStatus = () => {
  updateReadStatus(!props.note.read_status);
};
</script>
