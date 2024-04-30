<template>
  <div
    class="flex flex-wrap items-center gap-4 border-b border-gray-10 p-2 font-latin-sans"
    dir="ltr"
  >
    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton
        @toggle="editor?.chain().focus().addColumnAfter().run()"
      >
        <Icon
          class="rtl:rotate-180"
          name="mdi:table-column-plus-after"
          size="18"
        />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().addColumnBefore().run()"
      >
        <Icon
          class="rtl:rotate-180"
          name="mdi:table-column-plus-before"
          size="18"
        />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().deleteColumn().run()"
      >
        <Icon name="mdi:table-column-remove" size="18" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton @toggle="editor?.chain().focus().addRowAfter().run()">
        <Icon name="mdi:table-row-plus-after" size="18" />
      </EditorToggleButton>

      <EditorToggleButton
        @toggle="editor?.chain().focus().addRowBefore().run()"
      >
        <Icon name="mdi:table-row-plus-before" size="18" />
      </EditorToggleButton>

      <EditorToggleButton @toggle="editor?.chain().focus().deleteRow().run()">
        <Icon name="mdi:table-row-remove" size="18" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <EditorToggleButton
        :disabled="!editor?.can().mergeOrSplit()"
        @toggle="editor?.chain().focus().mergeOrSplit().run()"
      >
        <Icon
          v-if="editor?.can().splitCell()"
          name="mdi:table-split-cell"
          size="18"
        />

        <Icon v-else name="mdi:table-merge-cells" size="18" />
      </EditorToggleButton>
    </div>

    <div class="flex flex-wrap items-center gap-1">
      <PPopper show-arrow :offset="10">
        <EditorToggleButton>
          <Icon name="mdi:table-headers-eye" size="18" />
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
        <Icon name="mdi:table-remove" size="18" />
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
