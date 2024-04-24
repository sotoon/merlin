<template>
  <div class="flex h-8 w-8 items-center justify-center">
    <PLoading v-if="readStatusPending" class="text-primary" />

    <button
      v-else
      class="p-1 disabled:animate-pulse"
      @click.prevent="toggleReadStatus"
    >
      <Icon v-if="readStatus" class="text-gray-30" name="mdi:email-open" />
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

const readStatus = ref(props.note.read_status);

const toggleReadStatus = () => {
  updateReadStatus(!readStatus.value, {
    onSuccess: () => {
      readStatus.value = !readStatus.value;
    },
  });
};
</script>
