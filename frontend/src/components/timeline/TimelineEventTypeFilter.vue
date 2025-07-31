<template>
  <div class="flex flex-wrap items-center gap-2">
    <PListbox
      v-model="selectedEventTypes"
      multiple
      clearable
      hide-details
      :placeholder="t('timeline.filterByEventType')"
      size="small"
      class="w-48"
    >
      <PListboxOption
        v-for="eventType in eventTypes"
        :key="eventType.value"
        :label="eventType.label"
        :value="eventType.value"
      />
    </PListbox>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';

interface EventType {
  value: string;
  label: string;
}

interface Props {
  modelValue?: string[];
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:modelValue': [value: string[]];
}>();

const { t } = useI18n();

const eventTypes: EventType[] = [
  { value: 'SENIORITY_CHANGE', label: t('timeline.seniorityChange') },
  { value: 'PAY_CHANGE', label: t('timeline.payChange') },
  { value: 'BONUS_PAYOUT', label: t('timeline.bonusPayout') },
  { value: 'EVALUATION', label: t('timeline.evaluation') },
  { value: 'MAPPING', label: t('timeline.mapping') },
  { value: 'TITLE_CHANGE', label: t('timeline.titleChange') },
  { value: 'STOCK_GRANT', label: t('timeline.stockGrant') },
  { value: 'NOTICE', label: t('timeline.notice') },
];

const selectedEventTypes = computed({
  get() {
    return props.modelValue || [];
  },
  set(value: string[]) {
    emit('update:modelValue', value);
  },
});
</script>
