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

    <EditorLinkMenu v-if="editor" :editor="editor" />
  </div>
</template>

<script lang="ts" setup>
import { Link as TiptapLink } from '@tiptap/extension-link';
import { Underline as TiptapUnderline } from '@tiptap/extension-underline';
import TextDirection from 'tiptap-text-direction';

const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ 'update:model-value': [value: string] }>();

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    TiptapStarterKit,
    TiptapUnderline,
    TiptapLink.extend({
      inclusive: false,
    }).configure({
      openOnClick: false,
    }),
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

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>
