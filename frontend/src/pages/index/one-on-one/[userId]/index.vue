<script lang="ts" setup>
import { useRouteQuery } from '@vueuse/router';
import { computed } from 'vue';
import dayjs from '~/utils/dayjs';

defineProps<{ user: User }>();
definePageMeta({ name: 'one-on-one-userId' });

const search = useRouteQuery('q', '');
const sort = useRouteQuery('sort', ONE_ON_ONE_SORT_OPTION.newest);
const dateRangeQuery = useRouteQuery('date_range', '');
const dateRange = computed(() => {
  const value = dateRangeQuery.value as string;
  if (!value || value === '') return undefined;
  try {
    const parts = value.split(',');
    if (parts.length !== 2) return undefined;
    const [start, end] = parts;
    if (!start || !end) return undefined;

    const startDate = dayjs(start).toDate();
    const endDate = dayjs(end).toDate();

    return {
      from: startDate,
      to: endDate,
    };
  } catch {
    return undefined;
  }
});
</script>

<template>
  <div>
    <OneOnOneFilters>
      <OneOnOneSearchFilter />
      <template #sort>
        <OneOnOneSortControl />
      </template>
      <template #filter>
        <OneOnOneDateRangeFilter />
      </template>
    </OneOnOneFilters>
    <NoteOneOnOneList
      :user-id="user.uuid"
      :username="user.name"
      :search="search"
      :sort="sort"
      :date-range="dateRange"
    />
  </div>
</template>
