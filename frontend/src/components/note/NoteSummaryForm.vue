<template>
  <form class="space-y-10" @submit="onSubmit">
    <VeeField v-slot="{ value, handleChange }" name="content" rules="required">
      <Editor :model-value="value" @update:model-value="handleChange" />
    </VeeField>

    <div class="flex max-w-lg flex-col gap-6">
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
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

const props = defineProps<{
  summary?: NoteSummary;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [
    values: NoteSummaryFormValues,
    ctx: SubmissionContext<NoteSummaryFormValues>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteSummaryFormValues>({
  initialValues: {
    content: props.summary?.content || '',
    performance_label: props.summary?.performance_label,
    ladder_change: props.summary?.ladder_change || '',
    bonus: props.summary?.bonus,
    salary_change: props.summary?.salary_change,
    committee_date: props.summary?.committee_date
      ? new Date(props.summary?.committee_date)
      : undefined,
  },
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
