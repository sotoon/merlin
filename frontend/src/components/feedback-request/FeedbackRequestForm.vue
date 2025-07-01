<script lang="ts" setup>
import {
  PButton,
  PListbox,
  PListboxOption,
  PInput,
  PText,
  PDatePickerInput,
  PSwitch,
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';
import FeedbackRenderForm, {
  type FormQuestion,
} from './FeedbackRenderForm.vue';

const props = defineProps<{
  isSubmitting?: boolean;
  request?: Schema<'FeedbackRequestReadOnly'>;
}>();

const emit = defineEmits<{
  submit: [
    values: Schema<'FeedbackRequestWriteRequest'>,
    ctx: SubmissionContext<Schema<'FeedbackRequestWriteRequest'>>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit, setFieldValue, values } = useForm<
  Schema<'FeedbackRequestWriteRequest'>
>({
  initialValues: {
    title: props.request?.title || '',
    content: props.request?.content || '',
    requestee_emails: props.request?.requestees?.map((r) => r.email) || [],
    deadline: props.request?.deadline
      ? (new Date(props.request.deadline) as unknown as string)
      : null,
    form_uuid: props.request?.form_uuid || null,
  },
});

const { data: forms, isPending: isFormsLoading } = useGetFeedbackForms();

const onSubmit = handleSubmit((values, ctx) => {
  const deadline = values.deadline
    ? new Date(values.deadline).toISOString().split('T')[0]
    : null;

  emit('submit', { ...values, deadline }, ctx);
});

const isStructured = ref(!!props.request?.form_uuid);

watch(
  () => props.request,
  () => {
    isStructured.value = !!props.request?.form_uuid;
  },
);

watch(isStructured, (newValue) => {
  if (!newValue) {
    setFieldValue('form_uuid', null);
  }
});

// Get selected form schema
const selectedForm = computed(() => {
  return forms.value?.find((form) => form.uuid === values.form_uuid);
});
</script>

<template>
  <form class="flex flex-col gap-y-4" @submit="onSubmit">
    <VeeField v-slot="{ componentField }" name="title" rules="required">
      <PInput v-bind="componentField" :label="t('feedback.title')" required />
    </VeeField>

    <div>
      <label id="content-label">
        <PText class="block cursor-default" variant="caption1" weight="bold">
          {{ t('feedback.description') }}
        </PText>
      </label>
      <VeeField v-slot="{ value, handleChange }" name="content">
        <Editor
          :model-value="value"
          aria-labelledby="content-label"
          @update:model-value="handleChange"
        />
      </VeeField>
    </div>

    <PSwitch v-model="isStructured" :label="t('feedback.structuredFeedback')" />

    <VeeField
      v-if="isStructured"
      v-slot="{ componentField }"
      name="form_uuid"
      rules="required"
    >
      <PListbox
        v-bind="componentField"
        hide-details
        :label="t('feedback.selectForm')"
        :loading="isFormsLoading"
        required
      >
        <PListboxOption
          v-for="form in forms"
          :key="form.uuid"
          :label="form.title"
          :value="form.uuid"
        />
      </PListbox>
    </VeeField>

    <!-- Structured Form Preview -->
    <div v-if="isStructured && selectedForm">
      <PText class="mb-2 block" variant="caption1" weight="bold">
        {{ t('feedback.formPreview') }}
      </PText>
      <FeedbackRenderForm :schema="selectedForm.schema as FormQuestion[]" />
    </div>

    <VeeField v-slot="{ componentField }" name="requestee_emails">
      <UserSelect
        v-bind="componentField"
        :label="t('feedback.requestees')"
        multiple
      />
    </VeeField>

    <VeeField v-slot="{ componentField }" name="deadline">
      <PDatePickerInput
        v-bind="componentField"
        :label="t('feedback.deadline')"
        type="jalali"
      />
    </VeeField>

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
