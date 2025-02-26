<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-form text-h1 text-primary" />

      <PHeading level="h1" responsive>
        <!-- {{ t('note.createNewX', [noteTypeLabels[noteType]]) }} -->
      </PHeading>
    </div>
  </PBox>
</template>

<script setup>
import { PBox, PHeading } from '@pey/core';

definePageMeta({ name: 'form-assign' });
</script>
