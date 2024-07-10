<template>
  <PTabs v-model="selectedTab" class="rounded bg-white" variant="box">
    <PTab v-for="{ label, value } in typeOptions" :key="value" :title="label">
      <template v-if="newMessagesCounts[value ?? 'all']" #append>
        <div class="relative h-full w-1">
          <Badge
            class="absolute -left-2 top-0 -translate-x-1/2"
            :count="newMessagesCounts[value ?? 'all']"
            :max="99"
          />
        </div>
      </template>
    </PTab>
  </PTabs>
</template>

<script lang="ts" setup>
import { PTab, PTabs } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const typeFilter = useRouteQuery<string | undefined>('type', undefined);
const { data: messages } = useGetNotes({ retrieveMentions: true });

// TODO: filter out templates in the backend
const newMessagesCounts = computed(
  () =>
    messages.value
      ?.filter(
        (message) =>
          message.type !== NOTE_TYPE.template && !message.read_status,
      )
      .reduce<Partial<Record<NoteType | 'all', number>>>((acc, message) => {
        acc.all = (acc.all || 0) + 1;
        acc[message.type] = (acc[message.type] || 0) + 1;

        return acc;
      }, {}) || {},
);
const typeOptions = computed(() => [
  { label: t('common.all') },
  { label: t('noteType.goal'), value: NOTE_TYPE.goal },
  { label: t('noteType.task'), value: NOTE_TYPE.task },
  { label: t('noteType.meeting'), value: NOTE_TYPE.meeting },
  { label: t('noteType.proposal'), value: NOTE_TYPE.proposal },
  { label: t('common.feedback'), value: NOTE_TYPE.message },
]);
const selectedTab = computed({
  get() {
    return (
      typeOptions.value.findIndex((type) => type.value === typeFilter.value) ??
      0
    );
  },
  set(newValue) {
    typeFilter.value = typeOptions.value[newValue]?.value ?? undefined;
  },
});
</script>
