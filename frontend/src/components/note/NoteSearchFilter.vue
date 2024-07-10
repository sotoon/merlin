<template>
  <PInput
    v-model="query"
    hide-details
    :placeholder="t('common.search')"
    size="small"
    type="search"
  >
    <template #iconStart>
      <PeySearchIcon class="text-gray-50" :size="20" />
    </template>
  </PInput>
</template>

<script lang="ts" setup>
import { PInput } from '@pey/core';
import { PeySearchIcon } from '@pey/icons';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const query = useRouteQuery('q', '');
</script>
