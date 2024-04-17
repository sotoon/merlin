<template>
  <PText as="p" class="truncate">
    {{ editor?.getText().substring(0, 100) }}
  </PText>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

const props = defineProps<{ content: string }>();

const editor = useEditor({
  content: props.content,
  editable: false,
  extensions: [TiptapStarterKit],
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>
