<template>
  <div class="flex flex-wrap items-center gap-2">
    <PSwitch
      :model-value="isCurrentCycle"
      label="دوره فعلی؟"
      @update:model-value="updateCurrentCycle"
    />
  </div>
</template>

<script lang="ts" setup>
import { PSwitch } from '@pey/core';

const isCurrentCycle = useState<boolean>('isCurrentCycle');

function updateCurrentCycle(newValue: boolean) {
  isCurrentCycle.value = newValue;
}
</script>
