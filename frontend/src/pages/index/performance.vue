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
const { data: teams } = useGetTeams();
const { data: ladders } = useGetLadders();
const { data: tribes } = useGetTribes();
const { data: accessibleUsers } = useGetAccessibleUsers();
// const { data: profilePermissions } = useGetProfilePermissions();

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
    const column = columns.value.find((c) => c.key === key);

    if (
      filter.value === null ||
      filter.value === undefined ||
      filter.value === ''
    )
      continue;

    if (Array.isArray(filter.value)) {
      if (filter.value.length === 0) continue;
      filters[`${key}__in`] = filter.value.join(',');
    } else if (filter.condition) {
      let value = filter.value;
      if (column?.filter?.type === 'date') {
        value = dayjs(value).format('YYYY-MM-DD');
      }
      filters[`${key}__${filter.condition.toLowerCase()}`] = value;
    } else if (typeof filter.value === 'boolean') {
      filters[key] = filter.value ? 'true' : 'false';
    } else {
      filters[key] = filter.value;
    }
  }

  return {
    page: currentPage.value,
    ordering: ordering.value,
    ...filters,
  };
});

watch(
  () => [ordering.value, activeFilters.value],
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

const staticColumns = ref([
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

const dynamicColumns = computed(() => {
  if (!ladders.value || ladders.value.length === 0) return [];
  const selectedLadderCode = activeFilters.value.ladder?.value;
  if (!selectedLadderCode) return [];

  const selectedLadder = ladders.value.find(
    (l) => l.code === selectedLadderCode,
  );
  if (!selectedLadder) return [];

  return selectedLadder.aspects.map((aspect) => ({
    key: `aspect_${aspect.code}`,
    label: aspect.name,
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  }));
});

const columns = computed(() => {
  const overallLevelIndex = staticColumns.value.findIndex(
    (col) => col.key === 'overall_level',
  );

  if (overallLevelIndex === -1) {
    return [...staticColumns.value, ...dynamicColumns.value];
  }

  const firstPart = staticColumns.value.slice(0, overallLevelIndex + 1);
  const secondPart = staticColumns.value.slice(overallLevelIndex + 1);

  return [...firstPart, ...dynamicColumns.value, ...secondPart];
});

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
        <template
          v-for="col in dynamicColumns"
          :key="col.key"
          #[`cell-${col.key}`]="{ row }"
        >
          <PText variant="caption1">
            {{ row.ladder_levels[col.key.replace('aspect_', '')] }}
          </PText>
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
            searchable
            multiple
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
            searchable
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
        <template #filter-tribe="{ filter }">
          <PListbox
            v-model="filter.value"
            hide-details
            searchable
            multiple
            :label="t('common.allTribes')"
          >
            <PListboxOption
              v-for="tribe in tribes"
              :key="tribe.id"
              :label="tribe.name"
              :value="tribe.id"
            />
          </PListbox>
        </template>
        <template #filter-name="{ filter }">
          <PListbox
            v-model="filter.value"
            hide-details
            searchable
            multiple
            :label="t('common.allUsers')"
          >
            <PListboxOption
              v-for="user in accessibleUsers?.accessible_users"
              :key="user.id"
              :label="user.name || ''"
              :value="user.id"
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
