<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import {
  PButton,
  PHeading,
  PPagination,
  PBox,
  PText,
  PListbox,
  PListboxOption,
} from '@pey/core';
import {
  PeyRetryIcon,
  PeyCircleTickFilledIcon,
  PeyCircleCloseIcon,
} from '@pey/icons';
import CustomTable from '~/components/shared/CustomTable.vue';
import dayjs from '~/utils/dayjs';

interface SortBy {
  prop: string;
  order: 'ascending' | 'descending' | null;
}

definePageMeta({ name: 'performance-list' });

const { t } = useI18n();
const route = useRoute();
const { data: teams } = useGetTeams();
const { data: ladders } = useGetLadders();

const activeFilters = ref<Record<string, any>>({});

const sortBy = ref<SortBy>({ prop: '', order: null });
const ordering = computed(() => {
  if (!sortBy.value.order) return;
  return `${sortBy.value.order === 'ascending' ? '' : '-'}${sortBy.value.prop}`;
});

const currentPage = ref(1);
const params = computed(() => {
  const filters: Record<string, string> = {};
  for (const key in activeFilters.value) {
    const filter = activeFilters.value[key];
    if (Array.isArray(filter.value)) {
      filters[`${key}__in`] = filter.value.join(',');
    } else if (filter.condition) {
      filters[`${key}__${filter.condition.toLowerCase()}`] = filter.value;
    } else if (filter.value instanceof Date) {
      filters[key] = dayjs(filter.value).format('YYYY-MM-DD');
    } else if (typeof filter.value === 'boolean') {
      filters[key] = filter.value ? 'true' : 'false';
    } else {
      filters[key] = filter.value;
    }
  }

  console.log({ ...filters });

  return {
    page: currentPage.value,
    ordering: ordering.value,
    ...filters,
  };
});

watch(
  () => [
    route.query.team,
    route.query.ladder,
    ordering.value,
    route.query.as_of,
    activeFilters.value,
  ],
  () => {
    currentPage.value = 1;
  },
  { deep: true },
);

const { data, isPending, error, refetch } = useGetPerformanceList(params);

const totalItems = ref(0);
watch(
  data,
  (newData) => {
    if (newData?.count !== undefined) {
      totalItems.value = newData.count;
    }
  },
  { immediate: true },
);

useHead({
  title: t('common.performanceTable'),
});

const columns = ref([
  {
    key: 'index',
    label: '#',
    cellClass: 'w-12',
  },
  {
    key: 'name',
    label: 'نام',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'tribe',
    label: 'قبیله',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'team',
    label: 'تیم',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'is_mapped',
    label: 'مپ شده',
    sortable: true,
    filterable: true,
    filter: { type: 'boolean' as const },
  },
  {
    key: 'leader',
    label: 'لیدر',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'ladder',
    label: 'لدر',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'overall_level',
    label: 'سطح کلی',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'pay_band',
    label: 'پله حقوقی',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'salary_change',
    label: 'تغییر حقوق',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'committees_current_year',
    label: 'کمیته‌های سال جاری',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'committees_last_year',
    label: 'کمیته‌های سال گذشته',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'last_bonus_percentage',
    label: 'آخرین پاداش',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'last_bonus_date',
    label: 'آخرین تاریخ پاداش',
    sortable: true,
    filterable: true,
    filter: { type: 'date' as const },
  },
  {
    key: 'last_committee_date',
    label: 'آخرین تاریخ کمیته',
    sortable: true,
    filterable: true,
    filter: { type: 'date' as const },
  },
  {
    key: 'details',
    label: 'جزئیات',
  },
]);

const handleFilterChanged = (filters: Record<string, any>) => {
  activeFilters.value = filters;
};
</script>

<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <PHeading level="h1" responsive>
          {{ t('common.performanceTable') }}
        </PHeading>
      </div>

      <PerformanceExportButton />
    </div>

    <div v-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('user.getUsersError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <PBox v-else class="bg-white p-4">
      <CustomTable
        v-model:sort-by="sortBy"
        :columns="columns"
        :data="data?.results || []"
        :loading="isPending"
        class="border-none !shadow-none"
        @filter-changed="handleFilterChanged"
      >
        <template #cell-index="{ index }">
          <span
            class="flex h-6 w-6 items-center justify-center rounded-full bg-gray-10 text-sm font-bold"
          >
            {{ index + 1 }}
          </span>
        </template>
        <template #cell-last_committee_date="{ row }">
          <PText v-if="row.last_committee_date" variant="caption1">
            {{ new Date(row.last_committee_date).toLocaleDateString('fa-IR') }}
          </PText>
        </template>
        <template #cell-last_bonus_date="{ row }">
          <PText v-if="row.last_bonus_date" variant="caption1">
            {{ new Date(row.last_bonus_date).toLocaleDateString('fa-IR') }}
          </PText>
        </template>
        <template #cell-is_mapped="{ row }">
          <PeyCircleTickFilledIcon
            v-if="row.is_mapped"
            class="mx-auto h-5 w-5 text-success"
          />
          <PeyCircleCloseIcon v-else class="mx-auto h-5 w-5 text-warning" />
        </template>
        <template #cell-details="{ row }">
          <NuxtLink :to="{ name: 'user-detail', params: { id: row.uuid } }">
            <PButton size="small" color="primary">
              {{ t('common.details') }}
            </PButton>
          </NuxtLink>
        </template>
        <template #filter-team="{ filter }">
          <PListbox
            v-model="filter.value"
            hide-details
            :label="t('common.allTeams')"
          >
            <PListboxOption
              v-for="team in teams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </PListbox>
        </template>
        <template #filter-ladder="{ filter }">
          <PListbox
            v-model="filter.value"
            hide-details
            :label="t('common.allLadders')"
          >
            <PListboxOption
              v-for="ladder in ladders"
              :key="ladder.code"
              :label="ladder.name"
              :value="ladder.code"
            />
          </PListbox>
        </template>
      </CustomTable>

      <div class="mt-4 flex w-full items-center justify-end">
        <PPagination
          :total="totalItems"
          :page="currentPage"
          :show-size-picker="false"
          @page-change="({ page }) => (currentPage = page as unknown as number)"
        />
      </div>
    </PBox>
  </div>
</template>
