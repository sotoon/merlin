<template>
  <PBox class="px-3 py-2">
    <PSwitch
      :model-value="isCurrentCycle"
      :label="t('note.currentPeriod')"
      size="small"
      @update:model-value="updateCurrentCycle"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PSwitch, PBox } from '@pey/core';

const { t } = useI18n();
const isCurrentCycle = useState<boolean>('isCurrentCycle');

function updateCurrentCycle(newValue: boolean) {
  isCurrentCycle.value = newValue;
}
</script>
