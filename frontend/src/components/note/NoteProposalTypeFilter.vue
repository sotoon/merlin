<template>
  <PListbox
    v-model="proposalTypeModel"
    clearable
    hide-details
    size="small"
    placeholder="نوع کمیته"
  >
    <PListboxOption
      v-for="option in proposalTypeOptions"
      :key="option.value"
      :label="option.label"
      :value="option.value"
    />
  </PListbox>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();

const proposalTypeFilter = useRouteQuery<string | undefined>(
  'proposal_type',
  undefined,
);

const proposalTypeOptions = computed(() => [
  { label: t('proposalType.promotion'), value: PROPOSAL_TYPE.promotion },
  { label: t('proposalType.mapping'), value: PROPOSAL_TYPE.mapping },
  { label: t('proposalType.evaluation'), value: PROPOSAL_TYPE.evaluation },
]);

const proposalTypeModel = computed({
  get() {
    return proposalTypeFilter.value;
  },
  set(newValue) {
    proposalTypeFilter.value = newValue || undefined;
  },
});
</script>
