<template>
  <Transition
    class="transition-transform"
    enter-active-class="scale-0"
    leave-active-class="scale-0"
  >
    <PText
      v-if="count"
      class="block h-5 min-w-5 rounded-full bg-danger px-1.5 pt-0.5 text-center leading-normal text-white"
      dir="ltr"
      variant="caption2"
      weight="medium"
    >
      {{
        count <= max
          ? count.toLocaleString('fa-IR')
          : `${max.toLocaleString('fa-IR')}+`
      }}
    </PText>
  </Transition>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

withDefaults(defineProps<{ count?: number; max?: number }>(), {
  count: 0,
  max: 99,
});
</script>
