<template>
  <div
    class="overflow-hidden rounded border border-gray-10 bg-gray-00 transition focus-within:border-primary-50 focus-within:ring-4 focus-within:ring-primary-10 hover:border-gray-20 hover:focus-within:border-primary-50"
  >
    <EditorToolbar :editor="editor" />

    <div
      class="text-initial prose min-h-72 max-w-none cursor-text bg-white p-4 text-gray-100 transition [&_*]:outline-none"
      @click.self="editor?.commands.focus()"
    >
      <TiptapEditorContent :editor="editor" />
    </div>

    <EditorLinkMenu v-if="editor" :editor="editor" />
  </div>
</template>

<script lang="ts" setup>
import { Placeholder as TiptapPlaceholder} from '@tiptap/extension-placeholder';

import { useCustomEditor } from './useCustomEditor';

const props = defineProps<{ modelValue: string; placeholder?: string }>();
const emit = defineEmits<{ 'update:model-value': [value: string] }>();

const editor = useCustomEditor({
  extensions: [TiptapPlaceholder.configure({ placeholder: props.placeholder })],
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:model-value', editor.getHTML());
  },
});

watch(
  () => props.modelValue,
  (newModel) => {
    if (editor.value && newModel !== editor.value.getHTML()) {
      editor.value.commands.setContent(newModel);
    }
  },
);
</script>

<style>
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  position: absolute;
  color: #b6b6bd;
  pointer-events: none;
  height: 0;
}
</style>
