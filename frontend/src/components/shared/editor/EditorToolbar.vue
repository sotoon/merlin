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
        <i class="i-mdi-format-bold" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('italic')"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        @toggle="editor?.chain().focus().toggleItalic().run()"
      >
        <i class="i-mdi-format-italic" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('strike')"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        @toggle="editor?.chain().focus().toggleStrike().run()"
      >
        <i class="i-mdi-format-strikethrough" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('underline')"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        @toggle="editor?.chain().focus().toggleUnderline().run()"
      >
        <i class="i-mdi-format-underline" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('code')"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        @toggle="editor?.chain().focus().toggleCode().run()"
      >
        <i class="i-mdi-code-tags" />
      </EditorToggleButton>
    </div>

    <div class="ms-2 flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :active="editor.isActive('bulletList')"
        @toggle="editor?.chain().focus().toggleBulletList().run()"
      >
        <i class="i-mdi-format-list-bulleted" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('orderedList')"
        @toggle="editor?.chain().focus().toggleOrderedList().run()"
      >
        <i class="i-mdi-format-list-numbered" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('blockquote')"
        @toggle="editor?.chain().focus().toggleBlockquote().run()"
      >
        <i class="i-mdi-format-quote-close" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('codeBlock')"
        @toggle="editor?.chain().focus().toggleCodeBlock().run()"
      >
        <i class="i-mdi-code-block-tags" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().setHorizontalRule().run()"
      >
        <i class="i-mdi-horizontal-line" />
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
        <PeyLinkIcon :size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        v-if="!extendsToolbars?.includes('table')"
        :active="editor.isActive('table')"
        @toggle="
          editor?.isActive('table')
            ? editor.commands.focus()
            : editor
                ?.chain()
                .focus()
                .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
                .run()
        "
      >
        <i class="i-mdi-table" />
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
        <i v-if="editor.isActive({ dir: 'ltr' })" class="i-mdi-ltr" />
        <i v-else class="i-mdi-rtl" />
      </EditorToggleButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PeyLinkIcon } from '@pey/icons';

defineProps<{
  editor?: InstanceType<typeof TiptapEditor>;
  extendsToolbars?: string[];
}>();
</script>
