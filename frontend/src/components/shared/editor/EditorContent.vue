<template>
  <PScrollbar class="text-initial prose text-gray-100">
    <TiptapEditorContent :editor="editor" />
  </PScrollbar>
</template>

<script lang="ts" setup>
import { PScrollbar } from '@pey/core';
import { useCustomEditor } from './useCustomEditor';

const props = defineProps<{ content: string }>();

const editor = useCustomEditor({
  content: props.content,
  editable: false,
});

watch(
  () => props.content,
  (newContent) => {
    editor.value?.commands.setContent(newContent);
  },
);
</script>
