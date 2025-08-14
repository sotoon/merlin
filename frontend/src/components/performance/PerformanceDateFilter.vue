<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.date') }}:
    </PText>

    <PDatePickerInput
      v-model="selectedDate"
      type="jalali"
      hide-details
      size="small"
      :placeholder="t('common.selectDate')"
      @update:model-value="handleDateChange"
    />
  </div>
</template>

<script lang="ts" setup>
import { PDatePickerInput, PText } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';
import dayjs from '~/utils/dayjs';

const { t } = useI18n();

const dateQuery = useRouteQuery('as_of', '');
const selectedDate = ref<Date | undefined>(undefined);

const handleDateChange = (newValue: any) => {
  const query = { ...useRoute().query };

  if (newValue) {
    const formattedDate = dayjs(newValue).format('YYYY-MM-DD');
    query.as_of = formattedDate;
  } else {
    delete query.as_of;
  }

  useRouter().replace({ query });
};

onMounted(() => {
  const value = dateQuery.value as string;
  if (value && value !== '') {
    try {
      selectedDate.value = dayjs(value).toDate();
    } catch {
      selectedDate.value = undefined;
    }
  }
});

watch(
  () => useRoute().query.as_of,
  (newValue) => {
    if (newValue && typeof newValue === 'string') {
      try {
        selectedDate.value = dayjs(newValue).toDate();
      } catch {
        selectedDate.value = undefined;
      }
    } else {
      selectedDate.value = undefined;
    }
  },
  { immediate: true },
);
</script>
