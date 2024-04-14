<template>
  <div
    class="overflow-hidden rounded border border-gray-00 bg-gray-00 transition focus-within:border-primary-50 focus-within:ring-4 focus-within:ring-primary-10 hover:border-gray-20 hover:focus-within:border-primary-50"
  >
    <div
      v-if="editor"
      dir="ltr"
      class="flex flex-wrap gap-2 border-b border-gray-10 p-2"
    >
      <PButton
        type="button"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :color="editor.isActive('bold') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleBold().run()"
      >
        <strong>B</strong>
      </PButton>
      <PButton
        type="button"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :color="editor.isActive('italic') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleItalic().run()"
      >
        <em>i</em>
      </PButton>
      <PButton
        type="button"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        :color="editor.isActive('strike') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleStrike().run()"
      >
        <s>S</s>
      </PButton>
      <PButton
        type="button"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        :color="editor.isActive('underline') ? 'primary' : 'gray'"
        :variant="editor.isActive('underline') ? 'light' : 'ghost'"
        @click="editor?.chain().focus().toggleUnderline().run()"
      >
        <u>U</u>
      </PButton>
      <PButton
        type="button"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        :color="editor.isActive('code') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleCode().run()"
      >
        <code>{{ '<>' }}</code>
      </PButton>

      <PMenuButton @select="handleVariantSelect">
        <PButton type="button" :icon-end="PeyUnfoldMoreIcon" variant="ghost">
          {{ VARIANTS[selectedVariantIndex].label }}
        </PButton>

        <template #content>
          <PMenuButtonItem
            v-for="(variant, index) in VARIANTS"
            :key="index"
            :command="index"
            class="prose"
            dir="auto"
          >
            <component
              :is="variant.element"
              class="px-2"
              :class="{
                'text-primary': index === selectedVariantIndex,
                'text-gray-100': index !== selectedVariantIndex,
              }"
            >
              {{ variant.label }}
            </component>
          </PMenuButtonItem>
        </template>
      </PMenuButton>

      <PButton
        type="button"
        :color="editor.isActive('bulletList') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleBulletList().run()"
      >
        bullet list
      </PButton>
      <PButton
        type="button"
        :color="editor.isActive('orderedList') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleOrderedList().run()"
      >
        ordered list
      </PButton>
      <PButton
        type="button"
        :color="editor.isActive('codeBlock') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
      >
        code block
      </PButton>
      <PButton
        type="button"
        :color="editor.isActive('blockquote') ? 'primary' : 'gray'"
        variant="ghost"
        @click="editor?.chain().focus().toggleBlockquote().run()"
      >
        blockquote
      </PButton>
      <PButton
        type="button"
        variant="ghost"
        @click="editor?.chain().focus().setHorizontalRule().run()"
      >
        horizontal rule
      </PButton>
      <PButton
        type="button"
        variant="ghost"
        @click="editor?.chain().focus().setHardBreak().run()"
      >
        hard break
      </PButton>
      <PButton
        type="button"
        variant="ghost"
        @click="editor?.commands.setTextDirection('rtl')"
      >
        RTL
      </PButton>
      <PButton
        type="button"
        variant="ghost"
        @click="editor?.commands.setTextDirection('ltr')"
      >
        LTR
      </PButton>
    </div>

    <div
      class="prose max-w-none bg-white px-4 py-2 text-gray-100 transition [&_*]:outline-none"
      dir="rtl"
    >
      <TiptapEditorContent :editor="editor" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PMenuButton, PMenuButtonItem } from '@pey/core';
import { PeyUnfoldMoreIcon } from '@pey/icons';
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

const VARIANTS = [
  { label: 'Normal Text', element: 'p' },
  { label: 'Heading 1', element: 'h1' },
  { label: 'Heading 2', element: 'h2' },
  { label: 'Heading 3', element: 'h3' },
  { label: 'Heading 4', element: 'h4' },
] as const;

const selectedVariantIndex = computed({
  get() {
    const variantIndex = VARIANTS.findIndex(
      (_, index) =>
        index && editor.value?.isActive('heading', { level: index }),
    );
    return variantIndex > -1 ? variantIndex : 0;
  },
  set(index: number) {
    if (index === 0) {
      editor.value?.chain().focus().setParagraph().run();
    } else {
      // TODO: handle any type
      editor.value
        ?.chain()
        .focus()
        .setHeading({ level: index as any })
        .run();
    }
  },
});

const handleVariantSelect = (level: string | number) => {
  // TODO: handle assertion
  selectedVariantIndex.value = level as number;
};

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>
