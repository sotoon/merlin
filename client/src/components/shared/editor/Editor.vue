<template>
  <div
    class="overflow-hidden rounded border border-gray-00 bg-gray-00 transition focus-within:border-primary-50 focus-within:ring-4 focus-within:ring-primary-10 hover:border-gray-20 hover:focus-within:border-primary-50"
  >
    <EditorToolbar :editor="editor" />

    <div
      class="prose max-w-none bg-white px-4 py-2 text-gray-100 transition [&_*]:outline-none"
    >
      <TiptapEditorContent :editor="editor" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Underline as TiptapUnderline } from '@tiptap/extension-underline';
import TextDirection from 'tiptap-text-direction';

defineProps<{ name?: string }>();
const model = defineModel<string>({ default: '' });

const editor = useEditor({
  content: model.value,
  extensions: [
    TiptapStarterKit,
    TiptapUnderline,
    TextDirection.configure({
      types: [
        'heading',
        'paragraph',
        'blockquote',
        'bulletList',
        'orderedList',
        'codeBlock',
      ],
    }),
  ],
  onUpdate: ({ editor }) => {
    model.value = editor.getHTML();
  },
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>
