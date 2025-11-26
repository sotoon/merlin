<script lang="ts" setup>
import {
  PButton,
  PHeading,
  PPagination,
  PBox,
  PText,
  PListbox,
  PListboxOption,
  PInput,
  PDatePickerInput,
  PTooltip,
} from '@pey/core';
import {
  PeyRetryIcon,
  PeyCircleTickFilledIcon,
  PeyCircleCloseIcon,
  PeyCloudDownloadIcon,
  PeySearchIcon,
  PeyInfoIcon,
} from '@pey/icons';
import CustomTable from '~/components/shared/CustomTable.vue';
import dayjs from '~/utils/dayjs';
import { useDebounce } from '@vueuse/core';

interface SortBy {
  prop: string;
  order: 'ascending' | 'descending' | null;
}

definePageMeta({ name: 'performance-list' });

const { t } = useI18n();
const { $api } = useNuxtApp();
const { data: ladders } = useGetLadders();
const { data: accessibleUsers } = useGetAccessibleUsers();
const { data: profilePermissions } = useGetProfilePermissions();

const activeFilters = ref<Record<string, any>>({});
const nameSearch = ref('');
const debouncedNameSearch = useDebounce(nameSearch, 300);

const sortBy = ref<SortBy>({ prop: '', order: null });
const ordering = computed(() => {
  if (!sortBy.value.order) return;
  return `${sortBy.value.order === 'ascending' ? '' : '-'}${sortBy.value.prop}`;
});

const currentPage = ref(1);
const asOfDate = ref();
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
    } else if (column?.filter?.type === 'date-range') {
      if (filter.value && filter.value.from && filter.value.to) {
        filters[`${key}__gte`] = dayjs(filter.value.from)
          .startOf('day')
          .format('YYYY-MM-DD');
        filters[`${key}__lte`] = dayjs(filter.value.to)
          .endOf('day')
          .format('YYYY-MM-DD');
      }
    } else if (filter.condition) {
      filters[`${key}__${filter.condition.toLowerCase()}`] = filter.value;
    } else if (typeof filter.value === 'boolean') {
      filters[key] = filter.value ? 'true' : 'false';
    } else {
      filters[key] = filter.value;
    }
  }

  return {
    page: currentPage.value,
    ordering: ordering.value,
    name_search: debouncedNameSearch.value,
    as_of: asOfDate.value
      ? dayjs(asOfDate.value).format('YYYY-MM-DD')
      : undefined,
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

const isExporting = ref(false);
const handleExport = async () => {
  isExporting.value = true;
  try {
    const response = await $api.fetch.raw('/personnel/performance-table/csv/', {
      params: toValue(params.value),
    });

    const blob = new Blob([response._data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'performance-export.csv';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1];
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } finally {
    isExporting.value = false;
  }
};

useHead({
  title: t('common.performanceTable'),
});

const staticColumns = ref([
  {
    key: 'index',
    label: '#',
    cellClass: 'w-12',
    sticky: 'left' as const,
  },
  {
    key: 'name',
    label: 'نام',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
    sticky: 'left' as const,
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
    description: 'وضعیت مپینگ کاربرها (مپ شده یا نشده)',
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
    label: 'سطح لدر',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
  },
  {
    key: 'seniority_level',
    label: 'سطح سنیوریتی',
    sortable: true,
    filterable: true,
    filter: { type: 'string' as const },
  },
  {
    key: 'pay_band',
    label: 'پله حقوقی',
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
    description: 'تعداد کمیته‌ها از انواع مپینگ، ارتقا یا ارزیابی',
  },
  {
    key: 'committees_last_year',
    label: 'کمیته‌های سال گذشته',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
    description: 'تعداد کمیته‌ها از انواع مپینگ، ارتقا و ارزیابی',
  },
  {
    key: 'last_bonus_percentage',
    label: 'آخرین پاداش',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
    description: 'درصد آخرین پاداش دریافتی',
  },
  {
    key: 'salary_change',
    label: 'تغییر حقوق',
    sortable: true,
    filterable: true,
    filter: { type: 'numeric' as const },
    description: 'میزان تغییر حقوق در آخرین کمیته‌ی فرد',
  },
  {
    key: 'last_bonus_date',
    label: 'تاریخ آخرین پاداش',
    sortable: true,
    filterable: true,
    filter: { type: 'date-range' as const },
  },
  {
    key: 'last_salary_change_date',
    label: 'تاریخ آخرین تغییر حقوق',
    sortable: true,
    filterable: true,
    filter: { type: 'date-range' as const },
  },
  {
    key: 'last_committee_date',
    label: 'تاریخ آخرین کمیته',
    sortable: true,
    filterable: true,
    filter: { type: 'date-range' as const },
    description:
      'تاریخ آخرین کمیته‌ی برگزارشده از انواع: مپینگ، ارتقا یا ارزیابی',
  },
  {
    key: 'details',
    label: 'جزئیات',
    sticky: 'right' as const,
  },
]);

const accessibleLadders = computed(() => {
  return profilePermissions.value?.permissions.accessible_ladders;
});
const accessibleTribes = computed(() => {
  return profilePermissions.value?.permissions.accessible_tribes;
});
const accessibleTeams = computed(() => {
  return profilePermissions.value?.permissions.accessible_teams;
});
const accessibleLeaders = computed(() => {
  return profilePermissions.value?.permissions.accessible_leaders;
});

const selectedLadderName = computed(() => activeFilters.value.ladder?.value);
const selectedLadder = computed(() => {
  return ladders.value?.find((l) => l.name === selectedLadderName.value);
});

const dynamicColumns = computed(() => {
  if (
    !profilePermissions.value?.permissions.accessible_ladders ||
    profilePermissions.value?.permissions.accessible_ladders.length === 0
  )
    return [];

  if (!selectedLadder.value) return [];

  return selectedLadder.value.aspects.map((aspect) => ({
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
        <i class="i-mdi-chart-line text-h1 text-primary" />
        <PHeading level="h1" responsive>
          {{ t('common.performanceTable') }}
        </PHeading>
      </div>

      <PButton
        variant="light"
        size="small"
        :icon-start="PeyCloudDownloadIcon"
        :loading="isExporting"
        @click="handleExport"
      >
        {{ t('common.exportCSV') }}
      </PButton>
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
      <div class="flex items-start justify-between gap-2">
        <PInput
          v-model="nameSearch"
          class="w-full lg:w-1/4"
          placeholder="جستجوی نام"
        >
          <template #iconStart>
            <PeySearchIcon class="text-gray-50" :size="20" />
          </template>
        </PInput>

        <label class="flex items-center gap-2 text-md font-bold">
          <PDatePickerInput v-model="asOfDate" type="jalali" hide-details />
          <PTooltip>
            <PeyInfoIcon class="h-5 w-5 text-gray-50" />
            <template #content>
              <div class="font-normal max-w-sm">
                با انتخاب تاریخ در اینجا، تمام اطلاعات موجود در جدول بنا به
                تاریخی که وارد کردید به‌روزرسانی خواهندشد. به عنوان مثال با
                انتخاب تاریخ ۱۴۰۴/۰۶/۱۰ تمام مقادیر جدول به آخرین مقادیر معتبر
                در اون تاریخ تغییر خواهندکرد. (یعنی اگر در اون تاریخ به جدول
                نگاه می‌کردید این مقادیر رو می‌دیدید)
              </div>
            </template>
          </PTooltip>
        </label>
      </div>

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
            {{ ((currentPage - 1) * 10 + index + 1).toLocaleString('fa-IR') }}
          </span>
        </template>
        <template
          v-for="col in dynamicColumns"
          :key="col.key"
          #[`cell-${col.key}`]="{ row }"
        >
          <PText variant="caption1">
            {{
              row.ladder_levels[col.key.replace('aspect_', '')].toLocaleString(
                'fa-IR',
              )
            }}
          </PText>
        </template>
        <template #cell-last_committee_date="{ value }">
          <PText v-if="value" variant="caption1">
            {{ new Date(value).toLocaleDateString('fa-IR') }}
          </PText>
        </template>
        <template #cell-last_bonus_date="{ value }">
          <PText v-if="value" variant="caption1">
            {{ new Date(value).toLocaleDateString('fa-IR') }}
          </PText>
        </template>
        <template #cell-last_salary_change_date="{ value }">
          <PText v-if="value" variant="caption1">
            {{ new Date(value).toLocaleDateString('fa-IR') }}
          </PText>
        </template>
        <template #cell-is_mapped="{ value }">
          <PeyCircleTickFilledIcon
            v-if="value"
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
              v-for="team in accessibleTeams"
              :key="team"
              :label="team"
              :value="team"
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
              v-for="ladder in accessibleLadders"
              :key="ladder"
              :label="ladder"
              :value="ladder"
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
              v-for="tribe in accessibleTribes"
              :key="tribe"
              :label="tribe"
              :value="tribe"
            />
          </PListbox>
        </template>
        <template #filter-leader="{ filter }">
          <PListbox
            v-model="filter.value"
            hide-details
            searchable
            multiple
            :label="t('common.allLeaders')"
          >
            <PListboxOption
              v-for="leader in accessibleLeaders"
              :key="leader"
              :label="leader"
              :value="leader"
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
        <template
          v-for="col in dynamicColumns"
          :key="col.key"
          #[`filter-${col.key}`]="{ filter }"
        >
          <PListbox
            v-model="filter.value"
            hide-details
            searchable
            multiple
            :label="col.label"
          >
            <PListboxOption
              v-for="level in selectedLadder?.max_level"
              :key="level"
              :label="level.toLocaleString('fa-IR')"
              :value="level"
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
