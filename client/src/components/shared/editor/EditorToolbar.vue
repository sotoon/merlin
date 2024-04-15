<template>
  <div
    v-if="editor"
    class="font-latin-sans flex flex-wrap items-center gap-2 border-b border-gray-10 p-2"
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
    </div>

    <div class="ms-2 flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :active="editor.isActive({ dir: 'ltr' })"
        @toggle="editor?.commands.setTextDirection('ltr')"
      >
        <Icon name="ic:baseline-format-textdirection-l-to-r" size="20" />
      </EditorToggleButton>

      <EditorToggleButton
        :active="editor.isActive({ dir: 'rtl' })"
        @toggle="editor?.commands.setTextDirection('rtl')"
      >
        <Icon name="ic:baseline-format-textdirection-r-to-l" size="20" />
      </EditorToggleButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ editor?: InstanceType<typeof TiptapEditor> }>();
</script>
