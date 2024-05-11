<template>
  <div
    class="flex flex-wrap items-center gap-4 border-b border-gray-10 p-2 font-latin-sans"
    dir="ltr"
  >
    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton
        @toggle="editor?.chain().focus().addColumnAfter().run()"
      >
        <i class="i-mdi-table-column-plus-after rtl:rotate-180" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().addColumnBefore().run()"
      >
        <i class="i-mdi-table-column-plus-before rtl:rotate-180" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().deleteColumn().run()"
      >
        <i class="i-mdi-table-column-remove" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton @toggle="editor?.chain().focus().addRowAfter().run()">
        <i class="i-mdi-table-row-plus-after" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().addRowBefore().run()"
      >
        <i class="i-mdi-table-row-plus-before" />
      </EditorToggleButton>

      <EditorToggleButton @toggle="editor?.chain().focus().deleteRow().run()">
        <i class="i-mdi-table-row-remove" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :disabled="!editor?.can().mergeOrSplit()"
        @toggle="editor?.chain().focus().mergeOrSplit().run()"
      >
        <i v-if="editor?.can().splitCell()" class="i-mdi-table-split-cell" />
        <i v-else class="i-mdi-table-merge-cells" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <PPopper show-arrow :offset="10">
        <EditorToggleButton>
          <i class="i-mdi-table-headers-eye" />
        </EditorToggleButton>

        <template #content>
          <PBox class="space-y-3 bg-white p-3">
            <PSwitch
              :model-value="hasHeaderRow"
              label="Header row"
              size="small"
              @update:model-value="
                editor?.chain().focus().toggleHeaderRow().run()
              "
            />

            <PSwitch
              :model-value="hasHeaderColumn"
              label="Header column"
              size="small"
              @update:model-value="
                editor?.chain().focus().toggleHeaderColumn().run()
              "
            />
          </PBox>
        </template>
      </PPopper>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton @toggle="editor?.chain().focus().deleteTable().run()">
        <i class="i-mdi-table-remove" />
      </EditorToggleButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PBox, PPopper, PSwitch } from '@pey/core';

const props = defineProps<{ editor?: InstanceType<typeof TiptapEditor> }>();

const hasHeaderRow = computed(() =>
  Boolean(
    props.editor?.$node('table')?.firstChild?.lastChild?.node.type.name ===
      'tableHeader',
  ),
);
const hasHeaderColumn = computed(() =>
  Boolean(
    props.editor?.$node('table')?.lastChild?.firstChild?.node.type.name ===
      'tableHeader',
  ),
);
</script>
