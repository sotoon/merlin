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

const { t } = useI18n();
const route = useRoute();
const isExporting = ref(false);
const config = useRuntimeConfig();
const { data: teams } = useGetTeams();

const selectedTeam = computed(() => {
  return teams.value?.find((team) => team.name === route.query.team);
});

const handleExport = async () => {
  isExporting.value = true;

  try {
    const params = new URLSearchParams();

    if (selectedTeam.value)
      params.append('team', selectedTeam.value.id as unknown as string);
    if (route.query.ladder)
      params.append('ladder', route.query.ladder as string);
    if (route.query.ordering)
      params.append('ordering', route.query.ordering as string);
    if (route.query.q) params.append('q', route.query.q as string);
    if (route.query.as_of) params.append('as_of', route.query.as_of as string);

    params.append('format', 'csv');

    const downloadUrl = `${config.public.apiUrl}/personnel/performance-table/?${params.toString()}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `performance-table-${new Date().toISOString().split('T')[0]}.csv`;
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
