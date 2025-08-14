<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.ladder') }}:
    </PText>

    <div class="w-40">
      <PListbox v-model="selectedLadder" hide-details size="small">
        <PListboxOption :label="t('common.allLadders')" :value="''" />
        <PListboxOption
          v-for="ladder in ladders"
          :key="ladder.code"
          :label="ladder.name"
          :value="ladder.code"
        />
      </PListbox>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption, PText } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const selectedLadder = useRouteQuery('ladder', '');

const { data: ladders } = useGetLadders();

watch(selectedLadder, (newValue) => {
  const query = { ...useRoute().query };
  if (newValue) {
    query.ladder = newValue;
  } else {
    delete query.ladder;
  }
  useRouter().replace({ query });
});
</script>
