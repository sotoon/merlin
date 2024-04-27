<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="readStatusPending" class="text-white" />

    <button
      v-else
      class="rounded bg-primary p-1 text-white transition-colors hover:bg-primary-70 disabled:animate-pulse"
      @click="toggleReadStatus"
    >
      <Icon v-if="readStatus" class="opacity-50" name="mdi:email-open" />
      <Icon v-else name="mdi:email" />
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

const readStatus = ref(props.note.read_status);

const toggleReadStatus = () => {
  updateReadStatus(!readStatus.value, {
    onSuccess: () => {
      readStatus.value = !readStatus.value;
    },
  });
};
</script>
