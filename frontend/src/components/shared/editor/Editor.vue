<template>
  <div
    class="rounded border border-gray-10 transition focus-within:border-primary-50 focus-within:ring-4 focus-within:ring-primary-10 hover:border-gray-20 hover:focus-within:border-primary-50"
  >
    <div class="sticky top-0 z-[1] rounded-t bg-gray-00">
      <EditorToolbar :editor />

      <Transition
        class="transition-all"
        enter-from-class="max-h-0"
        enter-to-class="max-h-12"
        leave-from-class="max-h-12"
        leave-to-class="max-h-0"
      >
        <div v-if="editor?.isActive('table')" class="overflow-hidden">
          <EditorTableToolbar :editor />
        </div>
      </Transition>
    </div>

    <div
      class="text-initial prose flex min-h-72 max-w-none cursor-text flex-col rounded-b bg-white text-gray-100 transition [&_*]:outline-none"
    >
      <div class="h-4" @click.self="focusTop" />

      <TiptapEditorContent
        class="px-4"
        :editor
        @click.self="editor?.commands.focus()"
      />

      <div class="grow p-4" @click.self="editor?.commands.focus('end')" />
    </div>

    <EditorLinkMenu v-if="editor" :editor="editor" />
  </div>
</template>

<script lang="ts" setup>
import type { Editor } from '@tiptap/core';

import { Placeholder as TiptapPlaceholder } from '@tiptap/extension-placeholder';

import { useCustomEditor } from './useCustomEditor';
import { TrailingNode } from './TrailingNode';

const SCROLL_MARGIN = 120;

const props = defineProps<{ modelValue: string; placeholder?: string }>();
const emit = defineEmits<{ 'update:model-value': [value: string] }>();

const scrollIntoView = (editor: Editor) => {
  const { selection } = editor.state;

  if (!selection.empty) {
    return;
  }

  const viewportCoords = editor.view.coordsAtPos(selection.from);
  const absoluteOffset = window.scrollY + viewportCoords.top;

  if (viewportCoords.top < SCROLL_MARGIN) {
    window.scrollTo(window.scrollX, absoluteOffset - SCROLL_MARGIN);
  } else if (viewportCoords.top > window.innerHeight - SCROLL_MARGIN) {
    window.scrollTo(
      window.scrollX,
      absoluteOffset - window.innerHeight + SCROLL_MARGIN,
    );
  }
};

const editor = useCustomEditor({
  extensions: [
    TiptapPlaceholder.configure({ placeholder: props.placeholder }),
    TrailingNode,
  ],
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:model-value', editor.getHTML());
    scrollIntoView(editor);
  },
});

const focusTop = () => {
  editor.value?.commands.focus('start');

  if (!editor.value?.state.doc.firstChild?.type.isTextblock) {
    editor.value
      ?.chain()
      .focus()
      .insertContentAt(0, { type: 'paragraph' })
      .run();
  }
};

watch(
  () => props.modelValue,
  (newModel) => {
    if (editor.value && newModel !== editor.value.getHTML()) {
      editor.value.commands.setContent(newModel);
    }
  },
);
</script>
