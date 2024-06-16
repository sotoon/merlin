<template>
  <PBox class="flex flex-wrap items-center gap-8 bg-white p-4">
    <div v-if="slots.sort" class="flex flex-wrap items-center gap-2">
      <i class="i-mdi-sort text-h3 text-gray-50" />
      <slot name="sort" />
    </div>

    <div v-if="slots.filter" class="flex flex-wrap items-center gap-2">
      <PeyFilterIcon class="text-gray-50" />
      <slot name="filter" />
    </div>
  </PBox>
</template>

<script lang="ts" setup>
import { PBox } from '@pey/core';
import { PeyFilterIcon } from '@pey/icons';

const slots = defineSlots<{ sort?: any; filter?: any }>();
</script>
