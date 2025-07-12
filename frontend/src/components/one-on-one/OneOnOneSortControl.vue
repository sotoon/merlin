<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.sort') }}:
    </PText>

    <div class="w-36">
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
const sort = useRouteQuery('sort', ONE_ON_ONE_SORT_OPTION.newest);

const sortOptions = computed(() => [
  { label: t('note.newest'), value: ONE_ON_ONE_SORT_OPTION.newest },
  { label: t('note.oldest'), value: ONE_ON_ONE_SORT_OPTION.oldest },
  { label: t('note.title'), value: ONE_ON_ONE_SORT_OPTION.title },
]);

watch(
  [sort, sortOptions],
  () => {
    if (!sortOptions.value.some((option) => option.value === sort.value)) {
      sort.value = ONE_ON_ONE_SORT_OPTION.newest;
    }
  },
  { immediate: true },
);
</script>
