<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.sort') }}:
    </PText>

    <div class="w-40">
      <PListbox v-model="sort" hide-details size="small">
        <PListboxOption
          v-for="option in sortOptions"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </PListbox>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption, PText } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const sort = useRouteQuery('ordering', '-name');

const sortOptions = computed(() => [
  { label: t('common.name'), value: '-name' },
  { label: t('common.team'), value: '-team' },
  { label: t('common.overallLevel'), value: '-overall_level' },
  { label: t('common.payBand'), value: '-pay_band' },
  { label: t('common.lastBonus'), value: '-last_bonus_percentage' },
  { label: t('common.ladder'), value: '-ladder' },
  { label: t('common.leader'), value: '-leader' },
  { label: t('common.lastCommitteeDate'), value: '-last_committee_date' },
  {
    label: t('common.committeesCurrentYear'),
    value: '-committees_current_year',
  },
]);

// Watch sort changes and update URL
watch(sort, (newValue) => {
  const query = { ...useRoute().query };
  if (newValue && newValue !== '-name') {
    query.ordering = newValue;
  } else {
    delete query.ordering;
  }
  useRouter().replace({ query });
});
</script>
