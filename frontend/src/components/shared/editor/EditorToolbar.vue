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
        <Icon name="mdi:format-bold" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('italic')"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        @toggle="editor?.chain().focus().toggleItalic().run()"
      >
        <Icon name="mdi:format-italic" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('strike')"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        @toggle="editor?.chain().focus().toggleStrike().run()"
      >
        <Icon name="mdi:format-strikethrough" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('underline')"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        @toggle="editor?.chain().focus().toggleUnderline().run()"
      >
        <Icon name="mdi:format-underline" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('code')"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        @toggle="editor?.chain().focus().toggleCode().run()"
      >
        <Icon name="mdi:code-tags" size="18" />
      </EditorToggleButton>
    </div>

    <div class="ms-2 flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :active="editor.isActive('bulletList')"
        @toggle="editor?.chain().focus().toggleBulletList().run()"
      >
        <Icon name="mdi:format-list-bulleted" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('orderedList')"
        @toggle="editor?.chain().focus().toggleOrderedList().run()"
      >
        <Icon name="mdi:format-list-numbered" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('blockquote')"
        @toggle="editor?.chain().focus().toggleBlockquote().run()"
      >
        <Icon name="mdi:format-quote-close" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive('codeBlock')"
        @toggle="editor?.chain().focus().toggleCodeBlock().run()"
      >
        <Icon name="mdi:code-block-tags" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().setHorizontalRule().run()"
      >
        <Icon name="mdi:horizontal-line" size="18" />
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
        <Icon name="mdi:table" size="18" />
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
        <Icon v-if="editor.isActive({ dir: 'ltr' })" name="mdi:ltr" size="18" />
        <Icon v-else name="mdi:rtl" size="18" />
      </EditorToggleButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PeyLinkIcon } from '@pey/icons';

defineProps<{ editor?: InstanceType<typeof TiptapEditor> }>();
</script>
