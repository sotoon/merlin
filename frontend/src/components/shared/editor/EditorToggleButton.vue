<template>
  <PIconButton
    type="button"
    class="text-subtitle"
    :disabled="disabled"
    :icon="slots.default || icon"
    :color="active ? 'primary' : 'gray'"
    :variant="disabled ? 'ghost' : 'light'"
    @click="emit('toggle')"
  />
</template>

<script lang="ts" setup>
import { PIconButton } from '@pey/core';
import { PeyDoneIcon } from '@pey/icons';

const emit = defineEmits<{ toggle: [] }>();
withDefaults(
  defineProps<{ active?: boolean; disabled?: boolean; icon?: Component }>(),
  {
    icon: PeyDoneIcon,
  },
);
const slots = defineSlots<{ default?: () => any }>();
</script>
