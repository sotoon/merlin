<script lang="ts" setup>
import {
  PButton,
  PLoading,
  PText,
  PListbox,
  PListboxOption,
  PSwitch,
} from '@pey/core';
import { useForm } from 'vee-validate';
import FeedbackStructuredForm from './FeedbackStructuredForm.vue';

const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'cancel'): void;
}>();

const { t } = useI18n();
const { mutateAsync: createEntry, isPending } = useCreateAdhocFeedbackEntry();
const { data: forms, isPending: isFormsLoading } = useGetFeedbackForms();
const { data: users, pending: isUsersLoading } = useGetUsers();
const { data: profile } = useGetProfile();

const filteredUsers = computed(() => {
  if (!users.value) return [];
  if (!profile.value) return users.value;
  return users.value.filter((user) => user.email !== profile.value?.email);
});

const isStructured = ref(false);

// Form data for structured form
const structuredFormData = ref<Record<string, any>>({});

const { handleSubmit, meta, setFieldValue, values } = useForm<{
  receiver_id: string;
  content: string;
  evidence: string;
  form_uuid?: string;
  mentioned_users?: string[];
}>({
  initialValues: {
    receiver_id: '',
    content: '',
    evidence: '',
    form_uuid: '',
    mentioned_users: [],
  },
});

// Get selected form schema
const formSchema = computed(() => {
  if (!values.form_uuid || !forms.value) return undefined;
  const form = forms.value.find((f) => f.uuid === values.form_uuid);
  return form?.schema as FeedbackFormSchema;
});

const onSubmit = handleSubmit((values) => {
  // If it's a structured form, use the JSON stringified form data as content
  const content = isStructured.value
    ? JSON.stringify(structuredFormData.value, null, 2)
    : values.content;

  createEntry({
    content,
    mentioned_users: values.mentioned_users,
    evidence: isStructured.value ? '' : values.evidence,
    receiver_id: values.receiver_id,
    form_uuid: isStructured.value ? values.form_uuid : undefined,
  }).then(() => {
    emit('success');
  });
});

// Custom validation for structured forms
const isFormValid = computed(() => {
  if (!isStructured.value) {
    return meta.value.valid;
  }

  // Check if all required fields in structured form are filled
  if (!formSchema.value) return false;

  return formSchema.value.sections.every((section) => {
    return section.items.every((question) => {
      if (!question.required) return true;

      const value = structuredFormData.value[question.key];

      // Handle different question types
      switch (question.type) {
        case 'text':
          return value && typeof value === 'string' && value.trim() !== '';
        case 'likert':
          return value !== undefined && value !== null && value !== '';
        case 'multiple_choice':
          return Array.isArray(value) && value.length > 0;
        case 'sort':
          return Array.isArray(value) && value.length > 0;
        case 'tag':
          return Array.isArray(value) && value.length > 0;
        default:
          return value !== undefined && value !== null && value !== '';
      }
    });
  });
});

// Handle structured form updates
const handleStructuredFormUpdate = (formData: Record<string, any>) => {
  structuredFormData.value = formData;
};

watch(isStructured, (newValue) => {
  if (!newValue) {
    setFieldValue('form_uuid', '');
  }
});
</script>

<template>
  <form class="mt-4 space-y-4" @submit="onSubmit">
    <VeeField v-slot="{ componentField }" name="receiver_id" rules="required">
      <PListbox
        v-bind="componentField"
        hide-details
        :label="t('feedback.selectReceiver')"
        :loading="isUsersLoading"
        required
        searchable
      >
        <PListboxOption
          v-for="user in filteredUsers"
          :key="user.uuid"
          :label="user.name || user.email"
          :value="user.uuid"
        />
      </PListbox>
    </VeeField>

    <VeeField v-slot="{ componentField }" name="mentioned_users">
      <UserSelect
        v-bind="componentField"
        :label="t('note.mentionedUsers')"
        multiple
      />
    </VeeField>

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

    <div v-if="isStructured && formSchema">
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
            :model-value="value || ''"
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
            :model-value="value || ''"
            :placeholder="t('feedback.writeEvidenceContent')"
            aria-labelledby="feedback-evidence-label"
            @update:model-value="handleChange"
          />
        </VeeField>
      </div>
    </template>

    <div class="mt-4 flex items-center justify-end gap-4">
      <PLoading v-if="isPending" />
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
        :disabled="isPending || !isFormValid"
        :loading="isPending"
        type="submit"
        variant="fill"
      >
        {{ t('common.save') }}
      </PButton>
    </div>
  </form>
</template>
