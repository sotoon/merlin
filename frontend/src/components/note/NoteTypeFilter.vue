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

const props = defineProps<{ notes: Note[] }>();

const { t } = useI18n();
const typeFilter = useRouteQuery<string | undefined>('type', undefined);

// TODO: filter out templates in the backend
const newMessagesCounts = computed(
  () =>
    props.notes
      .filter(
        (message) =>
          message.type !== NOTE_TYPE.template &&
          message.type !== NOTE_TYPE.oneOnOne &&
          !message.read_status,
      )
      .reduce<Partial<Record<NoteType | 'all', number>>>((acc, message) => {
        acc.all = (acc.all || 0) + 1;
        if (message.type === NOTE_TYPE.feedbackRequest) {
          acc[NOTE_TYPE.feedback] = (acc[NOTE_TYPE.feedback] || 0) + 1;
        }
        acc[message.type] = (acc[message.type] || 0) + 1;
        return acc;
      }, {}) || {},
);
const typeOptions = computed(() => [
  { label: t('common.all') },
  { label: t('noteType.goal'), value: NOTE_TYPE.goal },
  { label: t('noteType.meeting'), value: NOTE_TYPE.meeting },
  { label: t('common.promotion'), value: NOTE_TYPE.proposal },
  { label: t('noteType.message'), value: NOTE_TYPE.message },
  { label: t('noteType.feedback'), value: NOTE_TYPE.feedback },
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
