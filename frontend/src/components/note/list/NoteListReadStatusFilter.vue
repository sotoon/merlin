<template>
  <PBox class="px-3 py-2">
    <PSwitch v-model="unreadModel" :label="t('note.unreadMessages')" />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PSwitch } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const unreadFilter = useRouteQuery('unread', undefined, {
  transform: (value) => value === 'true' || undefined,
});

const unreadModel = computed({
  get() {
    return Boolean(unreadFilter.value);
  },
  set(newValue) {
    unreadFilter.value = newValue || undefined;
  },
});
</script>
