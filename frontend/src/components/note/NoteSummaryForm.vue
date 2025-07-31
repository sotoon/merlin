<template>
  <form class="space-y-10" @submit="onSubmit">
    <VeeField v-slot="{ value, handleChange }" name="content" rules="required">
      <Editor
        :model-value="value"
        :placeholder="t('note.writeSummaryContent')"
        @update:model-value="handleChange"
      />
    </VeeField>

    <div v-if="ladderData?.aspects" class="max-w-lg space-y-6">
      <h3 class="text-gray-900 font-medium">
        {{ t('note.aspectChanges') }}
      </h3>

      <div
        v-for="(aspect, index) in ladderData?.aspects || []"
        :key="aspect.code"
        class="flex flex-wrap items-center gap-6 md:flex-row"
      >
        <div class="grow">
          <VeeField
            v-slot="{ componentField }"
            :name="`aspect_changes.${aspect.code}.new_level`"
            :rules="
              aspectCheckboxStates[index]
                ? 'required|min_value:1|max_value:10'
                : 'min_value:1|max_value:10'
            "
          >
            <PInput
              v-bind="componentField"
              :label="aspect.name"
              type="number"
              min="1"
              max="10"
              :required="aspectCheckboxStates[index]"
              :disabled="!aspectCheckboxStates[index]"
            />
          </VeeField>
        </div>

        <PCheckbox
          v-model="aspectCheckboxStates[index]"
          :label="t('note.hasChanged')"
          :value="true"
        />
      </div>
    </div>

    <div v-if="showCommitteeFields" class="flex max-w-lg flex-col gap-6">
      <div class="flex flex-col flex-wrap gap-6 md:flex-row">
        <div class="grow">
          <VeeField
            v-slot="{ componentField }"
            name="performance_label"
            rules="required"
          >
            <PListbox
              v-bind="componentField"
              :label="t('note.performanceLabel')"
              required
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
          <VeeField v-slot="{ componentField }" name="bonus" rules="required">
            <PInput
              v-bind="componentField"
              :label="t('note.performanceBonus')"
              prefix="%"
              required
              type="number"
            />
          </VeeField>
        </div>
      </div>

      <div class="flex flex-col flex-wrap gap-6 md:flex-row">
        <VeeField
          v-slot="{ componentField }"
          name="ladder_change"
          rules="required"
        >
          <PInput
            v-bind="componentField"
            class="grow"
            :label="t('note.ladderChange')"
            required
          />
        </VeeField>

        <div class="md:w-36">
          <VeeField
            v-slot="{ componentField }"
            name="salary_change"
            rules="required"
          >
            <PListbox
              v-bind="componentField"
              :label="t('note.salaryChange')"
              required
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
      </div>

      <div class="flex flex-col md:flex-row">
        <div>
          <VeeField v-slot="{ componentField }" name="committee_date">
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
  PCheckbox,
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

const props = defineProps<{
  summary?: Schema<'Summary'>;
  showCommitteeFields?: boolean;
  isSubmitting?: boolean;
  userUuid?: string;
}>();
const emit = defineEmits<{
  submit: [
    values: Schema<'SummaryRequest'>,
    ctx: SubmissionContext<Schema<'SummaryRequest'>>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { data: ladderData } = useGetCurrentLadder(props.userUuid);

const aspectCheckboxStates = ref<boolean[]>([]);
watch(
  ladderData,
  (newLadderData) => {
    if (newLadderData?.aspects) {
      // Initialize with existing values if editing, otherwise fill with false
      aspectCheckboxStates.value = newLadderData.aspects.map((aspect) => {
        return props.summary?.aspect_changes?.[aspect.code]?.changed || false;
      });
    }
  },
  { immediate: true },
);

const { meta, handleSubmit, values, setValues } = useForm<
  Schema<'SummaryRequest'>
>({
  initialValues: {
    content: props.summary?.content || '',
    aspect_changes: props.summary?.aspect_changes,
    performance_label: props.summary?.performance_label || undefined,
    ladder_change: props.summary?.ladder_change || '',
    bonus: props.summary?.bonus || undefined,
    salary_change: props.summary?.salary_change || undefined,
    committee_date: props.summary?.committee_date
      ? (new Date(props.summary?.committee_date) as unknown as string)
      : undefined,
  },
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});

watch(
  aspectCheckboxStates,
  (newStates) => {
    const newAspectChanges: Schema<'Summary'>['aspect_changes'] = {};

    ladderData.value?.aspects?.forEach((aspect, index) => {
      newAspectChanges[aspect.code] = {
        changed: newStates[index] || false,
        new_level: newStates[index]
          ? values.aspect_changes?.[aspect.code]?.new_level || 1
          : 1,
      };
    });

    setValues({ aspect_changes: newAspectChanges });
  },
  { deep: true },
);
</script>
