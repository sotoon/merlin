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

const props = defineProps<{ sortByDate?: boolean }>();

const { t } = useI18n();
const sort = useRouteQuery('sort', NOTE_SORT_OPTION.update);

const sortOptions = computed(() => [
  { label: t('note.lastEdit'), value: NOTE_SORT_OPTION.update },
  { label: t('note.newest'), value: NOTE_SORT_OPTION.newest },
  { label: t('note.oldest'), value: NOTE_SORT_OPTION.oldest },
  ...(props.sortByDate
    ? [{ label: t('note.meetingDate'), value: NOTE_SORT_OPTION.date }]
    : []),
  { label: t('note.title'), value: NOTE_SORT_OPTION.title },
]);

watch(
  [sort, sortOptions],
  () => {
    if (!sortOptions.value.some((option) => option.value === sort.value)) {
      sort.value = NOTE_SORT_OPTION.update;
    }
  },
  { immediate: true },
);
</script>
