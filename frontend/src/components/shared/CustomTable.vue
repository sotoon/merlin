<template>
  <div class="min-h-[500px] overflow-auto">
    <div class="flex">
      <!-- Left Sticky Columns -->
      <div
        v-if="leftStickyColumns.length > 0 && data.length > 0"
        class="shadow-xl"
      >
        <table class="w-full text-left text-sm rtl:text-right">
          <thead>
            <tr class="text-md text-gray-80">
              <th
                v-for="(column, index) in leftStickyColumns"
                :key="column.key || index"
                scope="col"
                tabindex="0"
                class="relative whitespace-nowrap bg-gray-10 px-4 first:rounded-s"
              >
                <div class="flex items-center">
                  <span
                    class="select-none text-md font-bold"
                    :class="{ 'cursor-pointer': column.sortable }"
                    @click="column.sortable && toggleSort(column.key)"
                  >
                    {{ column.label }}
                  </span>
                  <PTooltip v-if="column.description">
                    <PeyInfoFilledIcon class="mr-1 h-4 w-4 text-gray-40" />
                    <template #content>
                      {{ column.description }}
                    </template>
                  </PTooltip>
                  <span
                    v-if="column.sortable"
                    class="ms-1 inline-flex cursor-pointer flex-col"
                    :class="[
                      sortBy?.prop === column.key && sortBy.order
                        ? 'text-primary'
                        : 'text-gray-40',
                    ]"
                    @click="toggleSort(column.key)"
                  >
                    <PeyArrowDownFillIcon
                      class="-mb-3.5 h-5 w-5 rotate-180"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'ascending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                    <PeyArrowDownFillIcon
                      class="h-5 w-5"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'descending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                  </span>
                  <PPopper
                    v-if="column.filterable"
                    :model-value="openFilterKey === column.key"
                    class="ms-2"
                    placement="bottom"
                    @update:model-value="
                      (value) => (openFilterKey = value ? column.key : null)
                    "
                  >
                    <PeyFilterIcon
                      class="h-5 w-5 cursor-pointer text-gray-40"
                      :class="{
                        'text-primary': isFilterActive(column.key),
                      }"
                      @click="toggleFilterPopover(column.key)"
                    />
                    <template #content>
                      <div class="w-64 rounded-lg bg-white px-4 shadow-lg">
                        <slot
                          :name="`filter-${column.key}`"
                          :column="column"
                          :filter="stagedFilter"
                          :close="() => (openFilterKey = null)"
                        >
                          <div
                            v-if="
                              column.filter?.type === 'string' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PInput
                              v-model="stagedFilter.value"
                              :placeholder="`جستجو در ${column.label}`"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'numeric' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PListbox
                              v-model="stagedFilter.condition"
                              placeholder="شرط"
                              hide-details
                            >
                              <PListboxOption value="gt" label="بزرگتر" />
                              <PListboxOption value="lt" label="کوچکتر" />
                              <PListboxOption value="eq" label="برابر" />
                            </PListbox>
                            <PInput
                              v-model="stagedFilter.value"
                              type="number"
                              placeholder="مقدار"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PDatePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDate')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date-range' &&
                              stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PRangePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDateRange')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'boolean' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PSwitch
                              v-model="stagedFilter.value"
                              :label="column.label"
                            />
                          </div>
                        </slot>
                        <div class="mt-4 flex justify-end gap-2">
                          <PButton size="small" @click="applyFilter">
                            {{ t('common.apply') }}
                          </PButton>
                          <PButton
                            size="small"
                            color="gray"
                            @click="clearFilter"
                          >
                            {{ t('common.clear') }}
                          </PButton>
                        </div>
                      </div>
                    </template>
                  </PPopper>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in data" :key="rowIndex">
              <td
                v-for="(column, colIndex) in leftStickyColumns"
                :key="column.key || colIndex"
                tabindex="0"
                class="whitespace-nowrap border-b border-b-gray-10 bg-white px-4"
                :class="column.cellClass"
              >
                <slot
                  :name="`cell-${column.key}`"
                  :row="row"
                  :value="row[column.key]"
                  :index="rowIndex"
                >
                  {{
                    typeof row[column.key] === 'number'
                      ? row[column.key].toLocaleString('fa-IR')
                      : row[column.key]
                  }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Middle Scrollable Columns -->
      <div class="flex-1 overflow-x-auto">
        <table class="w-full text-left text-sm rtl:text-right">
          <thead>
            <tr class="text-md text-gray-80">
              <th
                v-for="(column, index) in middleColumns"
                :key="column.key || index"
                scope="col"
                tabindex="0"
                class="relative whitespace-nowrap bg-gray-10 px-4"
              >
                <div class="flex items-center">
                  <span
                    class="select-none text-md font-bold"
                    :class="{ 'cursor-pointer': column.sortable }"
                    @click="column.sortable && toggleSort(column.key)"
                  >
                    {{ column.label }}
                  </span>
                  <PTooltip v-if="column.description">
                    <PeyInfoFilledIcon class="mr-1 h-4 w-4 text-gray-40" />
                    <template #content>
                      {{ column.description }}
                    </template>
                  </PTooltip>
                  <span
                    v-if="column.sortable"
                    class="ms-1 inline-flex cursor-pointer flex-col"
                    :class="[
                      sortBy?.prop === column.key && sortBy.order
                        ? 'text-primary'
                        : 'text-gray-40',
                    ]"
                    @click="toggleSort(column.key)"
                  >
                    <PeyArrowDownFillIcon
                      class="-mb-3.5 h-5 w-5 rotate-180"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'ascending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                    <PeyArrowDownFillIcon
                      class="h-5 w-5"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'descending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                  </span>
                  <PPopper
                    v-if="column.filterable"
                    :model-value="openFilterKey === column.key"
                    class="ms-2"
                    placement="bottom"
                    @update:model-value="
                      (value) => (openFilterKey = value ? column.key : null)
                    "
                  >
                    <PeyFilterIcon
                      class="h-5 w-5 cursor-pointer text-gray-40"
                      :class="{
                        'text-primary': isFilterActive(column.key),
                      }"
                      @click="toggleFilterPopover(column.key)"
                    />
                    <template #content>
                      <div class="w-64 rounded-lg bg-white px-4 shadow-lg">
                        <slot
                          :name="`filter-${column.key}`"
                          :column="column"
                          :filter="stagedFilter"
                          :close="() => (openFilterKey = null)"
                        >
                          <div
                            v-if="
                              column.filter?.type === 'string' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PInput
                              v-model="stagedFilter.value"
                              :placeholder="`جستجو در ${column.label}`"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'numeric' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PListbox
                              v-model="stagedFilter.condition"
                              placeholder="شرط"
                              hide-details
                            >
                              <PListboxOption value="gt" label="بزرگتر" />
                              <PListboxOption value="lt" label="کوچکتر" />
                              <PListboxOption value="eq" label="برابر" />
                            </PListbox>
                            <PInput
                              v-model="stagedFilter.value"
                              type="number"
                              placeholder="مقدار"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PDatePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDate')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date-range' &&
                              stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PRangePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDateRange')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'boolean' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PSwitch
                              v-model="stagedFilter.value"
                              :label="column.label"
                            />
                          </div>
                        </slot>
                        <div class="mt-4 flex justify-end gap-2">
                          <PButton size="small" @click="applyFilter">
                            {{ t('common.apply') }}
                          </PButton>
                          <PButton
                            size="small"
                            color="gray"
                            @click="clearFilter"
                          >
                            {{ t('common.clear') }}
                          </PButton>
                        </div>
                      </div>
                    </template>
                  </PPopper>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="middleColumns.length" class="px-4 text-center">
                <PLoading class="mx-auto text-primary" :size="20" />
              </td>
            </tr>
            <tr v-else-if="!data || data.length === 0">
              <td
                :colspan="middleColumns.length"
                class="p-8 text-center text-gray-50"
              >
                <slot name="no-data">
                  <span>{{ t('common.noData') }}</span>
                </slot>
              </td>
            </tr>
            <tr v-for="(row, rowIndex) in data" v-else :key="rowIndex">
              <td
                v-for="(column, colIndex) in middleColumns"
                :key="column.key || colIndex"
                tabindex="0"
                class="whitespace-nowrap border-b border-b-gray-10 px-4"
                :class="column.cellClass"
              >
                <slot
                  :name="`cell-${column.key}`"
                  :row="row"
                  :value="row[column.key]"
                  :index="rowIndex"
                >
                  {{
                    typeof row[column.key] === 'number'
                      ? row[column.key].toLocaleString('fa-IR')
                      : row[column.key]
                  }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Right Sticky Columns -->
      <div
        v-if="rightStickyColumns.length > 0 && data.length > 0"
        class="shadow-xl"
      >
        <table class="w-full text-left text-sm rtl:text-right">
          <thead>
            <tr class="text-md text-gray-80">
              <th
                v-for="(column, index) in rightStickyColumns"
                :key="column.key || index"
                scope="col"
                tabindex="0"
                class="relative whitespace-nowrap bg-gray-10 px-4 last:rounded-e"
              >
                <div class="flex items-center">
                  <span
                    class="select-none text-md font-bold"
                    :class="{ 'cursor-pointer': column.sortable }"
                    @click="column.sortable && toggleSort(column.key)"
                  >
                    {{ column.label }}
                  </span>
                  <PTooltip v-if="column.description">
                    <PeyInfoFilledIcon class="mr-1 h-4 w-4 text-gray-40" />
                    <template #content>
                      {{ column.description }}
                    </template>
                  </PTooltip>
                  <span
                    v-if="column.sortable"
                    class="ms-1 inline-flex cursor-pointer flex-col"
                    :class="[
                      sortBy?.prop === column.key && sortBy.order
                        ? 'text-primary'
                        : 'text-gray-40',
                    ]"
                    @click="toggleSort(column.key)"
                  >
                    <PeyArrowDownFillIcon
                      class="-mb-3.5 h-5 w-5 rotate-180"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'ascending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                    <PeyArrowDownFillIcon
                      class="h-5 w-5"
                      :class="[
                        sortBy?.prop === column.key &&
                        sortBy?.order === 'descending'
                          ? 'opacity-100'
                          : 'opacity-40',
                      ]"
                    />
                  </span>
                  <PPopper
                    v-if="column.filterable"
                    :model-value="openFilterKey === column.key"
                    class="ms-2"
                    placement="bottom"
                    @update:model-value="
                      (value) => (openFilterKey = value ? column.key : null)
                    "
                  >
                    <PeyFilterIcon
                      class="h-5 w-5 cursor-pointer text-gray-40"
                      :class="{
                        'text-primary': isFilterActive(column.key),
                      }"
                      @click="toggleFilterPopover(column.key)"
                    />
                    <template #content>
                      <div class="w-64 rounded-lg bg-white px-4 shadow-lg">
                        <slot
                          :name="`filter-${column.key}`"
                          :column="column"
                          :filter="stagedFilter"
                          :close="() => (openFilterKey = null)"
                        >
                          <div
                            v-if="
                              column.filter?.type === 'string' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PInput
                              v-model="stagedFilter.value"
                              :placeholder="`جستجو در ${column.label}`"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'numeric' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PListbox
                              v-model="stagedFilter.condition"
                              placeholder="شرط"
                              hide-details
                            >
                              <PListboxOption value="gt" label="بزرگتر" />
                              <PListboxOption value="lt" label="کوچکتر" />
                              <PListboxOption value="eq" label="برابر" />
                            </PListbox>
                            <PInput
                              v-model="stagedFilter.value"
                              type="number"
                              placeholder="مقدار"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PDatePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDate')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'date-range' &&
                              stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PRangePickerInput
                              v-model="stagedFilter.value"
                              type="jalali"
                              hide-details
                              size="small"
                              :placeholder="t('common.selectDateRange')"
                              @keydown.enter="applyFilter"
                            />
                          </div>
                          <div
                            v-if="
                              column.filter?.type === 'boolean' && stagedFilter
                            "
                            class="space-y-2"
                          >
                            <PSwitch
                              v-model="stagedFilter.value"
                              :label="column.label"
                            />
                          </div>
                        </slot>
                        <div class="mt-4 flex justify-end gap-2">
                          <PButton size="small" @click="applyFilter">
                            {{ t('common.apply') }}
                          </PButton>
                          <PButton
                            size="small"
                            color="gray"
                            @click="clearFilter"
                          >
                            {{ t('common.clear') }}
                          </PButton>
                        </div>
                      </div>
                    </template>
                  </PPopper>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in data" :key="rowIndex">
              <td
                v-for="(column, colIndex) in rightStickyColumns"
                :key="column.key || colIndex"
                tabindex="0"
                class="whitespace-nowrap border-b border-b-gray-10 bg-white px-4"
                :class="column.cellClass"
              >
                <slot
                  :name="`cell-${column.key}`"
                  :row="row"
                  :value="row[column.key]"
                  :index="rowIndex"
                >
                  {{
                    typeof row[column.key] === 'number'
                      ? row[column.key].toLocaleString('fa-IR')
                      : row[column.key]
                  }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  PLoading,
  PPopper,
  PInput,
  PListbox,
  PListboxOption,
  PButton,
  PDatePickerInput,
  PSwitch,
  PTooltip,
  PRangePickerInput,
} from '@pey/core';
import {
  PeyArrowDownFillIcon,
  PeyFilterIcon,
  PeyInfoFilledIcon,
} from '@pey/icons';
import { ref, watch, computed } from 'vue';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  filter?: {
    type: 'string' | 'numeric' | 'date' | 'boolean' | 'date-range';
  };
  cellClass?: string;
  description?: string;
  sticky?: 'left' | 'right';
}

interface SortBy {
  prop: string;
  order: 'ascending' | 'descending' | null;
}

interface Props {
  columns: Column[];
  data: any[];
  sortBy?: SortBy;
  loading?: boolean;
}

const { t } = useI18n();
const props = defineProps<Props>();
const emit = defineEmits<{
  'update:sortBy': [value: SortBy];
  'filter-changed': [filters: Record<string, any>];
}>();

// Computed properties for the three column sections
const leftStickyColumns = computed(() =>
  props.columns.filter((col) => col.sticky === 'left'),
);

const rightStickyColumns = computed(() =>
  props.columns.filter((col) => col.sticky === 'right'),
);

const middleColumns = computed(() =>
  props.columns.filter((col) => !col.sticky),
);

const openFilterKey = ref<string | null>(null);
const stagedFilter = ref<any>(null);
const activeFilters = ref<Record<string, any>>({});

watch(openFilterKey, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // Reset local filter state when popover is closed
    stagedFilter.value = null;
  }
});

const isFilterActive = (key: string) => {
  const filter = activeFilters.value[key];
  if (!filter) return false;

  if (Array.isArray(filter.value)) {
    return filter.value.length > 0;
  }
  if (typeof filter.value === 'boolean') {
    return true;
  }
  if (
    filter.value &&
    typeof filter.value === 'object' &&
    'from' in filter.value &&
    'to' in filter.value
  ) {
    return !!(filter.value.from && filter.value.to);
  }
  return !!filter.value;
};

const toggleSort = (key: string) => {
  if (!key) return;

  if (props.sortBy?.prop !== key || !props.sortBy.order) {
    emit('update:sortBy', { prop: key, order: 'descending' });
  } else if (props.sortBy.order === 'descending') {
    emit('update:sortBy', { prop: key, order: 'ascending' });
  } else if (props.sortBy.order === 'ascending') {
    emit('update:sortBy', { prop: key, order: null });
  }
};

const toggleFilterPopover = (key: string) => {
  if (openFilterKey.value === key) {
    openFilterKey.value = null;
  } else {
    openFilterKey.value = key;
    const existingFilter = activeFilters.value[key];
    const column = props.columns.find((c) => c.key === key);

    if (existingFilter) {
      stagedFilter.value = JSON.parse(JSON.stringify(existingFilter));
      if (
        column?.filter?.type === 'date' &&
        stagedFilter.value.value &&
        typeof stagedFilter.value.value === 'string'
      ) {
        stagedFilter.value.value = new Date(stagedFilter.value.value);
      }
      if (column?.filter?.type === 'date-range' && stagedFilter.value.value) {
        if (
          stagedFilter.value.value.from &&
          typeof stagedFilter.value.value.from === 'string'
        ) {
          stagedFilter.value.value.from = new Date(
            stagedFilter.value.value.from,
          );
        }
        if (
          stagedFilter.value.value.to &&
          typeof stagedFilter.value.value.to === 'string'
        ) {
          stagedFilter.value.value.to = new Date(stagedFilter.value.value.to);
        }
      }
    } else {
      if (column?.filter?.type === 'numeric') {
        stagedFilter.value = { value: '', condition: 'eq' };
      } else if (column?.filter?.type === 'date') {
        stagedFilter.value = { value: null, condition: 'eq' };
      } else if (column?.filter?.type === 'date-range') {
        stagedFilter.value = { value: undefined };
      } else if (column?.filter?.type === 'boolean') {
        stagedFilter.value = { value: false };
      } else {
        stagedFilter.value = { value: '' };
      }
    }
  }
};

const applyFilter = () => {
  if (!openFilterKey.value) return;
  activeFilters.value[openFilterKey.value] = stagedFilter.value;
  emit('filter-changed', activeFilters.value);
  openFilterKey.value = null;
};

const clearFilter = () => {
  if (!openFilterKey.value) return;
  delete activeFilters.value[openFilterKey.value];
  emit('filter-changed', activeFilters.value);
  openFilterKey.value = null;
};
</script>

<style scoped>
/* Set fixed height for all rows to ensure consistency across sections */
tbody tr {
  height: 60px;
}

/* Ensure headers also have consistent height */
thead tr {
  height: 60px;
}

/* Ensure all cells have consistent padding and alignment */
th,
td {
  height: 60px;
  vertical-align: middle;
  box-sizing: border-box;
}
</style>
