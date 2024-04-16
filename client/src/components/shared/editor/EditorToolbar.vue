<template>
  <div
    v-if="editor"
    class="flex flex-wrap items-center gap-2 border-b border-gray-10 p-2 font-latin-sans"
    dir="ltr"
  >
    <div class="-me-2 w-32">
      <EditorTextNodeSelect :editor="editor" />
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :active="editor.isActive('bold')"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        @toggle="editor?.chain().focus().toggleBold().run()"
      >
        <strong>B</strong>
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('italic')"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        @toggle="editor?.chain().focus().toggleItalic().run()"
      >
        <em>i</em>
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('strike')"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        @toggle="editor?.chain().focus().toggleStrike().run()"
      >
        <s>S</s>
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('underline')"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        @toggle="editor?.chain().focus().toggleUnderline().run()"
      >
        <u>U</u>
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('code')"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        @toggle="editor?.chain().focus().toggleCode().run()"
      >
        <code>$</code>
      </EditorToggleButton>
    </div>

    <div class="ms-2 flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :active="editor.isActive('bulletList')"
        @toggle="editor?.chain().focus().toggleBulletList().run()"
      >
        <Icon name="ic:baseline-format-list-bulleted" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('orderedList')"
        @toggle="editor?.chain().focus().toggleOrderedList().run()"
      >
        <Icon name="ic:baseline-format-list-numbered" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('blockquote')"
        @toggle="editor?.chain().focus().toggleBlockquote().run()"
      >
        <Icon name="ic:baseline-format-quote" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('codeBlock')"
        @toggle="editor?.chain().focus().toggleCodeBlock().run()"
      >
        <Icon name="ic:baseline-code" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().setHorizontalRule().run()"
      >
        <Icon name="ic:baseline-horizontal-rule" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('link')"
        :disabled="!editor.isActive('link') && editor.state.selection.empty"
        @toggle="
          editor
            ?.chain()
            .focus()
            .setLink({ href: editor.getAttributes('link').href || '' })
            .run()
        "
      >
        <PeyLinkIcon :size="20" />
      </EditorToggleButton>
    </div>

    <div class="ms-2 flex flex-wrap items-center gap-1">
      <EditorToggleButton
        @toggle="
          editor
            ?.chain()
            .focus()
            .setTextDirection(editor.isActive({ dir: 'ltr' }) ? 'rtl' : 'ltr')
            .run()
        "
      >
        <Icon
          v-if="editor.isActive({ dir: 'ltr' })"
          name="ic:baseline-format-textdirection-l-to-r"
          size="20"
        />
        <Icon v-else name="ic:baseline-format-textdirection-r-to-l" size="20" />
      </EditorToggleButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PeyLinkIcon } from '@pey/icons';

defineProps<{ editor?: InstanceType<typeof TiptapEditor> }>();
</script>
