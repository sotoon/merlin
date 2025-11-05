<template>
  <form class="space-y-10" @submit="onSubmit">
    <VeeField v-slot="{ value, handleChange }" name="content" rules="required">
      <Editor
        :model-value="value"
        :placeholder="t('note.writeSummaryContent')"
        @update:model-value="handleChange"
      />
    </VeeField>

    <div v-if="ladders?.length && !isNotice" class="max-w-lg space-y-6">
      <VeeField
        v-slot="{ componentField }"
        name="ladder"
        :rules="isEvaluation ? '' : 'required'"
      >
        <PListbox
          v-bind="componentField"
          :required="!isEvaluation"
          :label="t('note.selectLadder')"
          :placeholder="t('note.selectLadderPlaceholder')"
          hide-details
          @update:model-value="onLadderChange"
        >
          <PListboxOption
            v-for="ladder in ladders"
            :key="ladder.code"
            :label="ladder.name"
            :value="ladder.code"
          >
            <div class="flex flex-col">
              <span class="font-medium">{{ ladder.name }}</span>
              <span class="text-gray-500 text-sm">
                {{ ladder.description }}
              </span>
            </div>
          </PListboxOption>
        </PListbox>
      </VeeField>

      <template v-if="currentAspects.length">
        <PAlert :title="t('note.aspectChangesAlertTitle')" variant="caution" />

        <h3 class="text-gray-900 font-medium">
          {{ t('note.aspectChanges') }}
        </h3>

        <div
          v-for="aspect in currentAspects"
          :key="aspect.code"
          class="flex flex-wrap items-end gap-6 md:flex-row"
        >
          <div class="flex gap-2">
            <VeeField
              v-slot="{ componentField }"
              :name="`aspect_changes.${aspect.code}.new_level`"
              :rules="
                isAspectChanged(aspect.code) && !isEvaluation
                  ? `required|min_value:1|max_value:${maxAspectLevelPossible(aspect.code)}`
                  : `min_value:1|max_value:${maxAspectLevelPossible(aspect.code)}`
              "
            >
              <PInput
                v-bind="componentField"
                :label="aspect.name"
                type="number"
                :min="1"
                :max="maxAspectLevelPossible(aspect.code)"
                hide-details
                class="w-32"
                :required="isAspectChanged(aspect.code) && !isEvaluation"
                :disabled="!isAspectChanged(aspect.code)"
                :placeholder="isAspectChanged(aspect.code) ? undefined : ''"
                :model-value="getAspectDisplayValue(aspect.code)"
              />
            </VeeField>

            <VeeField
              v-slot="{ componentField }"
              :name="`aspect_changes.${aspect.code}.stage`"
            >
              <PListbox
                v-bind="componentField"
                :label="t('note.stage')"
                hide-details
                :disabled="!isAspectChanged(aspect.code)"
              >
                <PListboxOption
                  v-for="stage in selectedLadder?.stages || []"
                  :key="stage.value"
                  :label="stage.label"
                  :value="stage.value"
                />
              </PListbox>
            </VeeField>
          </div>

          <PTooltip :disabled="!isAspectReachedMaxLevel(aspect.code)">
            <label class="mb-2 flex cursor-pointer items-center gap-2">
              <input
                type="checkbox"
                :checked="isAspectChanged(aspect.code)"
                :disabled="isAspectReachedMaxLevel(aspect.code)"
                class="text-primary-600 border-gray-300 focus:ring-primary-500 h-4 w-4 rounded bg-gray-100 focus:ring-2"
                @change="
                  (e) =>
                    toggleAspectChanged(
                      aspect.code,
                      (e.target as HTMLInputElement).checked,
                    )
                "
              />
              <span class="text-gray-700 text-sm font-medium">
                {{ t('note.hasChanged') }}
              </span>
            </label>
            <template #content>
              <PText variant="caption2">
                {{ t('note.aspectReachedMaxLevel') }}
              </PText>
            </template>
          </PTooltip>
        </div>
      </template>
    </div>

    <div v-if="showCommitteeFields" class="flex max-w-lg flex-col gap-6">
      <div v-if="!isNotice" class="flex flex-col flex-wrap gap-6 md:flex-row">
        <div v-if="isEvaluation" class="grow">
          <VeeField
            v-slot="{ componentField }"
            name="performance_label"
            rules="required"
          >
            <PListbox
              v-bind="componentField"
              :label="t('note.performanceLabel')"
              :required="isEvaluation"
            >
              <PListboxOption
                v-for="item in PERFORMANCE_LABELS"
                :key="item"
                :label="item"
                :value="item"
              />
            </PListbox>
          </VeeField>
        </div>

        <div class="md:w-36">
          <VeeField
            v-slot="{ componentField }"
            name="bonus"
            :rules="isEvaluation ? '' : 'required'"
          >
            <PInput
              v-bind="componentField"
              :label="t('note.performanceBonus')"
              prefix="%"
              :required="!isEvaluation"
              type="number"
            />
          </VeeField>
        </div>
      </div>

      <div class="flex flex-col flex-wrap gap-6 md:flex-row">
        <div v-if="!isNotice" class="md:w-36">
          <VeeField
            v-slot="{ componentField }"
            name="salary_change"
            :rules="isEvaluation ? '' : 'required'"
          >
            <PListbox
              v-bind="componentField"
              :label="t('note.salaryChange')"
              :required="!isEvaluation"
            >
              <PListboxOption
                v-for="change in SALARY_CHANGES"
                :key="change"
                :label="`${change}`"
                :value="change"
              />
            </PListbox>
          </VeeField>
        </div>
        <div>
          <VeeField
            v-slot="{ componentField }"
            name="committee_date"
            rules="required"
          >
            <PDatePickerInput
              v-bind="componentField"
              :label="t('note.committeeDate')"
              required
              type="jalali"
            />
          </VeeField>
        </div>
      </div>
    </div>

    <div class="flex flex-wrap items-center justify-end gap-4 pt-8">
      <PButton
        class="shrink-0"
        color="gray"
        type="button"
        variant="light"
        @click="emit('cancel')"
      >
        {{ t('common.cancel') }}
      </PButton>

      <PButton
        class="shrink-0"
        :disabled="!meta.valid || !meta.dirty || isSubmitting"
        :loading="isSubmitting"
        type="submit"
        variant="fill"
      >
        {{ t('common.save') }}
      </PButton>
    </div>
  </form>
</template>

<script lang="ts" setup>
import {
  PButton,
  PDatePickerInput,
  PInput,
  PListbox,
  PListboxOption,
  PAlert,
  PText,
  PTooltip,
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

const props = defineProps<{
  summary?: Schema<'Summary'>;
  showCommitteeFields?: boolean;
  isSubmitting?: boolean;
  note: Note;
}>();
const emit = defineEmits<{
  submit: [
    values: Schema<'SummaryRequest'>,
    ctx: SubmissionContext<Schema<'SummaryRequest'>>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { data: ladders } = useGetLadders();
const { data: currentLadder } = useGetLadderByUuid(props.note.owner_uuid);

const { meta, handleSubmit, values, setValues } = useForm<
  Schema<'SummaryRequest'>
>({
  initialValues: {
    content: props.summary?.content || '',
    aspect_changes: props.summary?.aspect_changes || {},
    ladder: props.summary?.ladder || '',
    performance_label: props.summary?.performance_label || undefined,
    bonus: props.summary?.bonus || undefined,
    salary_change: props.summary?.salary_change || undefined,
    committee_date: props.summary?.committee_date
      ? (new Date(props.summary?.committee_date) as unknown as string)
      : undefined,
  },
});

watch(currentLadder, (newLadder) => {
  if (newLadder) {
    setValues({ ladder: newLadder.ladder });
  }
});

const isEditing = computed(() => Boolean(props.summary));
useUnsavedChangesGuard({
  disabled: () => !meta.value.dirty || !isEditing.value,
});

const selectedLadder = computed(() => {
  if (!ladders.value || !values.ladder) return null;
  return ladders.value.find((ladder) => ladder.code === values.ladder);
});

const currentAspects = computed(() => {
  return selectedLadder.value?.aspects || [];
});

// Helper function to check if an aspect is changed
function isAspectChanged(aspectCode: string) {
  return values.aspect_changes?.[aspectCode]?.changed || false;
}

// Helper function to get display value for aspect inputs
function getAspectDisplayValue(aspectCode: string) {
  if (isAspectChanged(aspectCode)) {
    return values.aspect_changes?.[aspectCode]?.new_level || '';
  }
  return '';
}

// Function to toggle aspect changed state
function toggleAspectChanged(aspectCode: string, value: boolean) {
  const aspectChanges = { ...values.aspect_changes };

  if (!aspectChanges[aspectCode]) {
    aspectChanges[aspectCode] = {
      changed: false,
      new_level: 1,
      stage: undefined,
    };
  }

  aspectChanges[aspectCode] = {
    ...aspectChanges[aspectCode],
    changed: value,
    new_level: value ? aspectChanges[aspectCode].new_level || 1 : 1,
    stage: value ? aspectChanges[aspectCode].stage || undefined : undefined,
  };

  setValues({ aspect_changes: aspectChanges });
}

// Handle ladder selection change
function onLadderChange(ladderCode: string) {
  if (ladderCode && ladders.value) {
    const ladder = ladders.value.find((l) => l.code === ladderCode);
    if (ladder) {
      const allAspectChanges = { ...values.aspect_changes };

      ladder.aspects.forEach((aspect) => {
        const summaryAspect = props.summary?.aspect_changes?.[aspect.code];
        allAspectChanges[aspect.code] = {
          changed: summaryAspect?.changed || false,
          new_level: summaryAspect?.new_level || 1,
          stage: summaryAspect?.stage || undefined,
        };
      });

      // Reset all previous aspects to changed: false
      Object.keys(allAspectChanges).forEach((aspectCode) => {
        if (!ladder.aspects.find((aspect) => aspect.code === aspectCode)) {
          allAspectChanges[aspectCode] = {
            changed: false,
            new_level: 1,
            stage: undefined,
          };
        }
      });

      // Clean up aspects that have changed: true but no new_level
      Object.keys(allAspectChanges).forEach((aspectCode) => {
        const aspect = allAspectChanges[aspectCode];
        if (aspect.changed && !aspect.new_level) {
          allAspectChanges[aspectCode] = {
            changed: false,
            new_level: 1,
            stage: undefined,
          };
        }
      });

      setValues({ aspect_changes: allAspectChanges });
    }
  }
}

const isEvaluation = computed(
  () => props.note.proposal_type === PROPOSAL_TYPE.evaluation,
);
const isNotice = computed(
  () => props.note.proposal_type === PROPOSAL_TYPE.notice,
);

function maxAspectLevelPossible(aspectCode: string) {
  if (!currentLadder.value || !selectedLadder.value) return 0;

  if (selectedLadder.value.code == currentLadder.value.ladder) {
    return (
      currentLadder.value.max_level -
      (currentLadder.value.current_aspects?.[aspectCode] || 0)
    );
  }

  return selectedLadder.value.max_level;
}

function isAspectReachedMaxLevel(aspectCode: string) {
  return maxAspectLevelPossible(aspectCode) === 0;
}

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
