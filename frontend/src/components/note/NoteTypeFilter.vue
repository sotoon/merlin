<template>
  <div class="w-28">
    <PListbox
      :model-value="typeFilter"
      clearable
      hide-details
      :placeholder="t('note.type')"
      size="small"
      @update:model-value="
        (value) => (typeFilter = value === '' ? undefined : value)
      "
    >
      <PListboxOption
        v-for="{ label, value } in typeOptions"
        :key="value"
        :label="label"
        :value="value"
      />
    </PListbox>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const typeFilter = useRouteQuery<string>('type', undefined);

const typeOptions = computed(() => [
  { label: t('noteType.goal'), value: NOTE_TYPE.goal },
  { label: t('noteType.task'), value: NOTE_TYPE.task },
  { label: t('noteType.meeting'), value: NOTE_TYPE.meeting },
  { label: t('noteType.proposal'), value: NOTE_TYPE.proposal },
  { label: t('noteType.message'), value: NOTE_TYPE.message },
]);
</script>
