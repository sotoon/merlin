<template>
  <TiptapBubbleMenu
    :editor="editor"
    :tippy-options="{
      duration: 100,
      placement: 'bottom',
      onShown: () => {
        if (!editor.getAttributes('link').href) {
          isEditMode = true;
        }
      },
    }"
    :should-show="handleShouldShow"
  >
    <PBox class="w-64 bg-white p-2 sm:w-80" dir="ltr">
      <form
        v-if="isEditMode || !linkUrl"
        class="flex items-center gap-2"
        @submit.prevent="handleLinkFormSubmit"
      >
        <PInput
          v-model="linkUrl"
          autofocus="true"
          class="grow"
          hide-details
          name="url"
          size="small"
          type="url"
        >
          <template #iconStart>
            <PeyLinkIcon :size="20" />
          </template>
        </PInput>

        <PIconButton
          color="gray"
          :icon="PeyDoneIcon"
          size="small"
          variant="light"
        />

        <PIconButton
          type="button"
          color="gray"
          :icon="PeyCloseIcon"
          size="small"
          variant="light"
          @click="handleLinkFormCancel"
        />
      </form>

      <div v-else class="flex justify-between gap-4 overflow-hidden">
        <div class="flex items-center gap-2 overflow-hidden">
          <PeyEarthIcon class="hidden shrink-0 sm:block" :size="20" />

          <PLink
            class="truncate font-latin-sans"
            :href="linkUrl"
            rel="noopener noreferrer nofollow"
            target="_blank"
            :title="linkUrl"
            variant="caption1"
            weight="medium"
          >
            {{ linkUrl }}
          </PLink>
        </div>

        <div class="flex items-center gap-1">
          <PIconButton
            type="button"
            color="gray"
            :icon="PeyEditIcon"
            size="small"
            variant="ghost"
            @click="isEditMode = true"
          />

          <PIconButton
            type="button"
            color="gray"
            :icon="PeyTrashIcon"
            size="small"
            variant="ghost"
            @click="handleRemoveLink"
          />
        </div>
      </div>
    </PBox>
  </TiptapBubbleMenu>
</template>

<script lang="ts" setup>
import { PBox, PIconButton, PInput, PLink } from '@pey/core';
import {
  PeyCloseIcon,
  PeyDoneIcon,
  PeyEditIcon,
  PeyEarthIcon,
  PeyTrashIcon,
  PeyLinkIcon,
} from '@pey/icons';
import { isMarkActive } from '@tiptap/core';

const props = defineProps<{ editor: InstanceType<typeof TiptapEditor> }>();

const isEditMode = ref(false);
const linkUrl = ref(props.editor.getAttributes('link').href);

const handleShouldShow = () => {
  // !FIX: workaround used from https://github.com/ueberdosis/tiptap/issues/4870#issuecomment-1954825623
  return isMarkActive(props.editor.view.state, 'link');
};

const handleLinkFormSubmit = () => {
  if (!linkUrl.value) {
    return;
  }

  props.editor
    .chain()
    .extendMarkRange('link')
    .setLink({ href: linkUrl.value })
    .run();
  isEditMode.value = false;
};

const handleLinkFormCancel = () => {
  linkUrl.value = props.editor.getAttributes('link').href;
  isEditMode.value = false;
  if (!linkUrl.value) {
    props.editor.commands.unsetLink();
  }
};

const handleRemoveLink = () => {
  props.editor.commands.unsetLink();
  isEditMode.value = false;
};

const handleSelectionUpdate = () => {
  linkUrl.value = props.editor.getAttributes('link').href;

  if (props.editor.isActive('link')) {
    isEditMode.value = !linkUrl.value;
  }
};

onMounted(() => {
  props.editor.on('selectionUpdate', handleSelectionUpdate);
});

onBeforeUnmount(() => {
  props.editor.off('selectionUpdate', handleSelectionUpdate);
});
</script>
