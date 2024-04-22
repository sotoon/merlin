<template>
  <div>
    <div class="flex h-10 flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
        <Icon class="text-gray-50" name="mdi:sort" role="presentation" />

        <PText class="text-gray-50" variant="caption2">
          {{ t('common.sort') }}:
        </PText>

        <div class="w-36">
          <PListbox v-model="sortModel" hide-details size="small">
            <PListboxOption
              v-for="(option, index) in sortOptions"
              :key="index"
              :label="option.label"
              :value="option.value"
            />
          </PListbox>
        </div>
      </div>

      <PeyFilterIcon class="text-gray-50" />

      <div class="flex items-center gap-2">
        <div class="w-24">
          <PListbox
            :model-value="yearFilter"
            clearable
            hide-details
            :placeholder="t('note.year')"
            size="small"
            @update:model-value="
              (value) => (yearFilter = value === '' ? undefined : value)
            "
          >
            <PListboxOption
              v-for="year in yearOptions"
              :key="year"
              :label="year.toLocaleString('fa-IR', { useGrouping: false })"
              :value="year"
            />
          </PListbox>
        </div>
      </div>

      <div class="w-24">
        <PListbox
          :model-value="periodFilter"
          clearable
          hide-details
          :placeholder="t('note.period')"
          size="small"
          @update:model-value="
            (value) => (periodFilter = value === '' ? undefined : value)
          "
        >
          <PListboxOption
            v-for="(period, index) in EVALUATION_PERIODS"
            :key="index"
            :label="period"
            :value="index"
          />
        </PListbox>
      </div>
    </div>

    <ul
      v-if="sortedNotes.length"
      class="mt-4 grid grid-cols-1 gap-2 py-4 lg:grid-cols-2 lg:gap-3"
    >
      <li v-for="note in sortedNotes" :key="note.uuid">
        <NuxtLink
          :to="
            note.type === 'Template'
              ? {
                  name: 'template',
                  params: {
                    id: note.uuid,
                  },
                }
              : {
                  name: 'note',
                  params: {
                    type: route.params.type || '-',
                    id: note.uuid,
                  },
                }
          "
        >
          <NoteCard
            :note="note"
            :display-writer="displayWriter"
            :display-type="displayType"
          />
        </NuxtLink>
      </li>
    </ul>

    <PText v-else as="p" class="mt-8 text-center text-gray-70" responsive>
      {{ t('note.noNotes') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption, PText } from '@pey/core';
import { PeyFilterIcon } from '@pey/icons';
import { useRouteQuery } from '@vueuse/router';

const props = defineProps<{
  notes: Note[];
  displayWriter?: boolean;
  displayType?: boolean;
}>();

const { t } = useI18n();
const route = useRoute();

const sortOptions = [
  { label: t('note.lastEdit'), value: NOTE_SORT_OPTION.update },
  { label: t('note.evaluationPeriod'), value: NOTE_SORT_OPTION.period },
  { label: t('common.date'), value: NOTE_SORT_OPTION.date },
];

const yearOptions = computed(() =>
  [...new Set(props.notes.map((note) => note.year))].sort((a, b) => b - a),
);

const yearFilter = useRouteQuery('year', undefined, {
  transform: (value) => (value ? Number(value) : undefined),
});
const periodFilter = useRouteQuery('period', undefined, {
  transform: (value) => (value ? Number(value) : undefined),
});

const filteredNotes = computed(() =>
  props.notes.filter(
    (note) =>
      note.year === (yearFilter.value ?? note.year) &&
      note.period === (periodFilter.value ?? note.period),
  ),
);

const { sortModel, sortedNotes } = useSortNotes(filteredNotes);
</script>
