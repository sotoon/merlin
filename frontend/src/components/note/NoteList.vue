<template>
  <div>
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-2">
        <Icon class="text-gray-50" name="mdi:sort" role="presentation" />

        <PText class="text-gray-50" variant="caption2">
          {{ t('common.sort') }}:
        </PText>

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

    <ul class="mt-4 grid grid-cols-1 gap-2 py-4 lg:grid-cols-2 lg:gap-3">
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
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption, PText } from '@pey/core';

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

const { sortModel, sortedNotes } = useSortNotes(props.notes);
</script>
