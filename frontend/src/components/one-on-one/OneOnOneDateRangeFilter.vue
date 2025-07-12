<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.dateRange') }}:
    </PText>

    <PRangePickerInput
      v-model="dateRange"
      type="jalali"
      hide-details
      size="small"
      :placeholder="t('common.selectDateRange')"
      @update:model-value="handleDateRangeChange"
    />
  </div>
</template>

<script lang="ts" setup>
import { PRangePickerInput, PText } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';
import { ref, onMounted, watch } from 'vue';
import dayjs from '~/utils/dayjs';

const { t } = useI18n();

// Use route query for date range
const dateRangeQuery = useRouteQuery('date_range', '');
const dateRange = ref<any>(undefined);

// Handle date range changes
const handleDateRangeChange = (newValue: any) => {
  const query = { ...useRoute().query };

  if (newValue && newValue.from && newValue.to) {
    // Set start time to 00:00:00 and end time to 23:59:59 using dayjs format
    const startDate = dayjs(newValue.from)
      .startOf('day')
      .format('YYYY-MM-DDTHH:mm:ss');
    const endDate = dayjs(newValue.to)
      .endOf('day')
      .format('YYYY-MM-DDTHH:mm:ss');

    query.date_range = `${startDate},${endDate}`;
  } else {
    delete query.date_range;
  }

  useRouter().replace({ query });
};

// Initialize date range from URL
onMounted(() => {
  const value = dateRangeQuery.value as string;
  if (value && value !== '') {
    try {
      const parts = value.split(',');
      if (parts.length === 2) {
        const [start, end] = parts;
        if (start && end) {
          // Convert gregorian dates back to Date objects for the picker
          dateRange.value = {
            from: dayjs(start).toDate(),
            to: dayjs(end).toDate(),
          };
        }
      }
    } catch {
      dateRange.value = undefined;
    }
  }
});

// Watch URL changes and update date range
watch(
  () => useRoute().query.date_range,
  (newValue) => {
    if (newValue && typeof newValue === 'string') {
      try {
        const parts = newValue.split(',');
        if (parts.length === 2) {
          const [start, end] = parts;
          if (start && end) {
            dateRange.value = {
              from: dayjs(start).toDate(),
              to: dayjs(end).toDate(),
            };
          }
        }
      } catch {
        dateRange.value = undefined;
      }
    } else {
      dateRange.value = undefined;
    }
  },
  { immediate: true },
);
</script>
