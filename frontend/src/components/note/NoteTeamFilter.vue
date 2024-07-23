<template>
  <PBox class="px-3 py-2">
    <PSwitch v-model="myTeamModel" :label="t('common.myTeam')" size="small" />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PSwitch } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const myTeamFilter = useRouteQuery('my-team', undefined, {
  transform: (value) => value === 'true' || undefined,
});

const myTeamModel = computed({
  get() {
    return Boolean(myTeamFilter.value);
  },
  set(newValue) {
    myTeamFilter.value = newValue || undefined;
  },
});
</script>
