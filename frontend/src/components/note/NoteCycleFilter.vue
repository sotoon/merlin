<template>
  <PBox class="px-3 py-2">
    <PSwitch
      v-model="isCurrentCycle"
      :label="t('note.currentPeriod')"
      size="small"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PSwitch, PBox } from '@pey/core';

const { t } = useI18n();
const isCurrentCycle = defineModel<boolean>();
</script>
