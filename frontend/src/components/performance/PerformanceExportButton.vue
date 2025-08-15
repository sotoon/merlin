<template>
  <PButton
    variant="light"
    size="small"
    :icon-start="PeyCloudDownloadIcon"
    :loading="isExporting"
    @click="handleExport"
  >
    {{ t('common.exportCSV') }}
  </PButton>
</template>

<script lang="ts" setup>
import { PButton } from '@pey/core';
import { PeyCloudDownloadIcon } from '@pey/icons';

interface Props {
  filters: Record<string, any>;
}
const props = defineProps<Props>();

const { t } = useI18n();
const isExporting = ref(false);
const config = useRuntimeConfig();

const handleExport = async () => {
  isExporting.value = true;

  try {
    const params = new URLSearchParams();

    for (const key in props.filters) {
      if (key === 'page') continue;
      const value = props.filters[key];
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    }

    params.append('format', 'csv');

    const downloadUrl = `${config.public.apiUrl}/personnel/performance-table/?${params.toString()}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `performance-table-${
      new Date().toISOString().split('T')[0]
    }.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Export failed:', error);
  } finally {
    isExporting.value = false;
  }
};
</script>
