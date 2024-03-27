<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<!-- eslint-disable vue/no-v-html -->
<template>
  <div>
    <div class="flex items-center justify-between gap-4">
      <PHeading class="px-4" responsive>
        {{ note.title }}
      </PHeading>

      <PIconButton
        class="shrink-0"
        :icon="PeyEditIcon"
        type="button"
        @click="navigateTo({ name: 'note-edit' })"
      />
    </div>

    <div class="p-4" v-html="note.content" />
  </div>
</template>

<script lang="ts" setup>
import { PHeading, PIconButton } from '@pey/core';
import { PeyEditIcon } from '@pey/icons';

defineProps<{ note: Note }>();
</script>
