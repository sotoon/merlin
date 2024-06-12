<template>
  <NuxtLink v-if="note" class="*:cursor-pointer" :to="noteLinkTo">
    <PChip
      color="primary"
      :icon="PeyLinkIcon"
      :label="note.title"
      size="small"
    />
  </NuxtLink>
</template>

<script lang="ts" setup>
import { PChip } from '@pey/core';
import { PeyLinkIcon } from '@pey/icons';

const props = defineProps<{ noteId: string }>();

const { data: note } = useGetNote({ id: props.noteId });

const noteLinkTo = computed(() => {
  if (!note.value) {
    return undefined;
  }

  if (note.value.type === NOTE_TYPE.template) {
    return {
      name: 'template',
      params: { id: note.value.uuid },
    };
  }

  if (note.value.type === NOTE_TYPE.message) {
    return {
      name: 'feedback',
      params: { id: note.value.uuid },
    };
  }

  return {
    name: 'note',
    params: {
      type: NOTE_TYPE_ROUTE_PARAM[note.value.type],
      id: note.value.uuid,
    },
  };
});
</script>
