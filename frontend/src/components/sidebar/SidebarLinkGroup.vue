<template>
  <div>
    <PText as="h1" class="py-1 ps-2" variant="subtitle">
      {{ title }}
    </PText>

    <hr class="border-gray-10" />

    <ul class="mt-2 space-y-0.5">
      <slot />
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

defineProps<{ title: string }>();
</script>
