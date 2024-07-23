<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.sort') }}:
    </PText>

    <div class="w-36">
      <PListbox v-model="sort" hide-details size="small">
        <PListboxOption
          v-for="(option, index) in sortOptions"
          :key="index"
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

const sortOptions = [
  { label: t('note.lastEdit'), value: NOTE_SORT_OPTION.update },
  { label: t('note.newest'), value: NOTE_SORT_OPTION.newest },
  { label: t('note.oldest'), value: NOTE_SORT_OPTION.oldest },
  { label: t('note.evaluationPeriod'), value: NOTE_SORT_OPTION.period },
  ...(props.sortByDate
    ? [{ label: t('note.meetingDate'), value: NOTE_SORT_OPTION.date }]
    : []),
  { label: t('note.title'), value: NOTE_SORT_OPTION.title },
];
</script>
