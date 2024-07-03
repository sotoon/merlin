<template>
  <PTabs v-model="selectedTab" class="rounded bg-white" variant="box">
    <PTab v-for="{ label, value } in typeOptions" :key="value" :title="label" />
  </PTabs>
</template>

<script lang="ts" setup>
import { PTab, PTabs } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const typeFilter = useRouteQuery<string | undefined>('type', undefined);

const typeOptions = computed(() => [
  { label: t('common.all') },
  { label: t('noteType.goal'), value: NOTE_TYPE.goal },
  { label: t('noteType.task'), value: NOTE_TYPE.task },
  { label: t('noteType.meeting'), value: NOTE_TYPE.meeting },
  { label: t('noteType.proposal'), value: NOTE_TYPE.proposal },
  { label: t('noteType.message'), value: NOTE_TYPE.message },
]);
const selectedTab = computed({
  get() {
    return (
      typeOptions.value.findIndex((type) => type.value === typeFilter.value) ??
      0
    );
  },
  set(newValue) {
    typeFilter.value = typeOptions.value[newValue]?.value ?? undefined;
  },
});
</script>
