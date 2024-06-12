<template>
  <div class="flex flex-wrap items-center gap-2">
    <div class="w-24">
      <PListbox
        :model-value="yearFilter"
        clearable
        hide-details
        :placeholder="t('note.year')"
        size="small"
        @update:model-value="
          (value) => (yearFilter = value === '' ? undefined : value)
        "
      >
        <PListboxOption
          v-for="year in yearOptions"
          :key="year"
          :label="year.toLocaleString('fa-IR', { useGrouping: false })"
          :value="year"
        />
      </PListbox>
    </div>

    <div class="w-24">
      <PListbox
        :model-value="periodFilter"
        clearable
        hide-details
        :placeholder="t('note.period')"
        size="small"
        @update:model-value="
          (value) => (periodFilter = value === '' ? undefined : value)
        "
      >
        <PListboxOption
          v-for="(period, index) in EVALUATION_PERIODS"
          :key="index"
          :label="period"
          :value="index"
        />
      </PListbox>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const props = defineProps<{ notes: Note[] }>();

const { t } = useI18n();

const yearOptions = computed(() =>
  [...new Set(props.notes.map((note) => note.year))].sort((a, b) => b - a),
);

const yearFilter = useRouteQuery('year', undefined, {
  transform: (value) => (value ? Number(value) : undefined),
});
const periodFilter = useRouteQuery('period', undefined, {
  transform: (value) => (value ? Number(value) : undefined),
});
</script>
