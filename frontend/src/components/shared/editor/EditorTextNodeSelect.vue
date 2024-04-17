<template>
  <PMenuButton @select="handleTypeSelect">
    <PButton
      type="button"
      :color="selectedTypeIndex > 0 ? 'primary' : 'gray'"
      :disabled="disabled"
      :icon-end="PeyUnfoldMoreIcon"
      size="small"
      :variant="disabled ? 'ghost' : 'light'"
    >
      {{ TEXT_NODE_TYPES[selectedTypeIndex]?.label || 'Normal Text' }}
    </PButton>

    <template #content>
      <PMenuButtonItem
        v-for="(variant, index) in TEXT_NODE_TYPES"
        :key="index"
        :command="index"
        class="prose"
        dir="auto"
      >
        <component
          :is="variant.element"
          class="px-2"
          :class="{
            'text-primary': index === selectedTypeIndex,
            'text-gray-100': index !== selectedTypeIndex,
          }"
        >
          {{ variant.label }}
        </component>
      </PMenuButtonItem>
    </template>
  </PMenuButton>
</template>

<script lang="ts" setup>
import { PButton, PMenuButton, PMenuButtonItem } from '@pey/core';
import { PeyUnfoldMoreIcon } from '@pey/icons';

const TEXT_NODE_TYPES = [
  { label: 'Normal Text', element: 'p', type: 'paragraph' },
  { label: 'Heading 1', element: 'h1', type: 'heading', level: 1 },
  { label: 'Heading 2', element: 'h2', type: 'heading', level: 2 },
  { label: 'Heading 3', element: 'h3', type: 'heading', level: 3 },
  { label: 'Heading 4', element: 'h4', type: 'heading', level: 4 },
] as const;

const props = defineProps<{ editor: InstanceType<typeof TiptapEditor> }>();

const selectedTypeIndex = computed({
  get() {
    return TEXT_NODE_TYPES.findIndex((nodeType) =>
      props.editor.isActive(
        nodeType.type,
        'level' in nodeType ? { level: nodeType.level } : undefined,
      ),
    );
  },
  set(index) {
    const nodeType = TEXT_NODE_TYPES[index];

    if (nodeType.type === 'paragraph') {
      props.editor.chain().focus().setParagraph().run();
    } else {
      props.editor.chain().focus().setHeading({ level: nodeType.level }).run();
    }
  },
});
const disabled = computed(() => selectedTypeIndex.value < 0);

const handleTypeSelect = (level: string | number) => {
  if (typeof level === 'string') {
    return;
  }
  selectedTypeIndex.value = level;
};
</script>
