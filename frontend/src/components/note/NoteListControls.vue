<template>
  <div class="flex flex-wrap items-center gap-4">
    <div v-if="slots.sort" class="flex flex-wrap items-center gap-2">
      <Icon class="text-gray-50" name="mdi:sort" role="presentation" />
      <slot name="sort" />
    </div>

    <div v-if="slots.filter" class="flex flex-wrap items-center gap-2">
      <PeyFilterIcon class="text-gray-50" />
      <slot name="filter" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PeyFilterIcon } from '@pey/icons';

const slots = defineSlots<{ sort?: any; filter?: any }>();
</script>
