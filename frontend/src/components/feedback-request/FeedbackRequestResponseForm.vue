<script lang="ts" setup>
import { PButton, PLoading, PText } from '@pey/core';
import { useForm } from 'vee-validate';
import FeedbackStructuredForm from './FeedbackStructuredForm.vue';

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
}>();

const emit = defineEmits<{
  (e: 'success'): void;
}>();

const { t } = useI18n();
const { mutateAsync: createEntry, isPending } = useCreateFeedbackEntry(
  props.request.uuid,
);

// Get feedback forms to find the selected form
const { data: forms } = useGetFeedbackForms();

// Check if this request has a structured form
const hasStructuredForm = computed(() => !!props.request.form_uuid);

// Get the selected form schema
const formSchema = computed(() => {
  if (!hasStructuredForm.value || !forms.value || !props.request.form_uuid)
    return undefined;
  const form = forms.value.find(
    (form) => form.uuid === props.request.form_uuid,
  );
  return form?.schema as FeedbackFormSchema;
});

// Form data for structured form
const structuredFormData = ref<Record<string, any>>({});

const { handleSubmit, meta } = useForm<{ content: string; evidence: string }>({
  initialValues: {
    content: '',
    evidence: '',
  },
});

const onSubmit = handleSubmit((values) => {
  // If it's a structured form, use the JSON stringified form data as content
  const content = hasStructuredForm.value
    ? JSON.stringify(structuredFormData.value, null, 2)
    : values.content;

  createEntry({
    content,
    evidence: hasStructuredForm.value ? '' : values.evidence,
    feedback_request_uuid: props.request.uuid,
    receiver_id: props.request.owner_uuid,
  }).then(() => {
    emit('success');
  });
});

// Custom validation for structured forms
const isFormValid = computed(() => {
  if (!hasStructuredForm.value) {
    return meta.value.valid;
  }

  // Check if all required fields in structured form are filled
  if (!formSchema.value) return false;

  return formSchema.value.sections.every((section) => {
    return section.items.every((question) => {
      return structuredFormData.value[question.key] !== undefined;
    });
  });
});

// Handle structured form updates
const handleStructuredFormUpdate = (formData: Record<string, any>) => {
  structuredFormData.value = formData;
};
</script>

<template>
  <form
    class="mt-4 space-y-4 rounded-md border border-gray-20 p-4"
    @submit="onSubmit"
  >
    <div v-if="hasStructuredForm && formSchema">
      <FeedbackStructuredForm
        :schema="formSchema"
        @update="handleStructuredFormUpdate"
      />
    </div>

    <template v-else>
      <div>
        <label id="feedback-content-label" class="mb-2 block">
          <PText class="cursor-default" variant="caption1" weight="bold">
            {{ t('feedback.writeFeedback') }}
            <span class="text-danger">*</span>
          </PText>
        </label>
        <VeeField
          v-slot="{ value, handleChange }"
          name="content"
          rules="required"
        >
          <Editor
            :model-value="value"
            :placeholder="t('feedback.writeFeedbackContent')"
            autofocus
            aria-labelledby="feedback-content-label"
            @update:model-value="handleChange"
          />
        </VeeField>
      </div>

      <div>
        <label id="feedback-evidence-label" class="mb-2 block">
          <PText class="cursor-default" variant="caption1" weight="bold">
            {{ t('feedback.evidence') }}
          </PText>
        </label>
        <VeeField v-slot="{ value, handleChange }" name="evidence">
          <Editor
            :model-value="value"
            :placeholder="t('feedback.writeEvidenceContent')"
            aria-labelledby="feedback-evidence-label"
            @update:model-value="handleChange"
          />
        </VeeField>
      </div>
    </template>

    <div class="mt-4 flex items-center justify-end gap-4">
      <PLoading v-if="isPending" />
      <PButton type="submit" :disabled="isPending || !isFormValid">
        {{ t('common.submit') }}
      </PButton>
    </div>
  </form>
</template>
