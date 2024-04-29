<template>
  <Transition
    class="transition-transform"
    enter-active-class="scale-0"
    leave-active-class="scale-0"
  >
    <PText
      v-if="count"
      class="absolute left-4 block min-h-5 min-w-5 rounded-full bg-danger px-1.5 pt-0.5 text-center text-white"
      variant="caption2"
      weight="medium"
    >
      {{ count.toLocaleString('fa-IR') }}
    </PText>
  </Transition>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

defineProps<{ count?: number }>();
</script>
