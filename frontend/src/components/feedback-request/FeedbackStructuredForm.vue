<script setup lang="ts">
import { PText, PChip, PListbox, PListboxOption } from '@pey/core';
import { useForm } from 'vee-validate';

const props = defineProps<{
  schema: SchemaQuestion[];
}>();

const emit = defineEmits<{
  (e: 'update', value: Record<string, any>): void;
}>();

const { t } = useI18n();

// Create dynamic form fields based on schema
const formFields = computed(() => {
  const fields: Record<string, any> = {};
  props.schema.forEach((question, index) => {
    fields[`question_${index}`] = '';
  });
  return fields;
});

const { values } = useForm({
  initialValues: formFields.value,
});

// Watch for changes and emit the form data
watch(
  values,
  (newValues) => {
    const formData: Record<string, any> = {};
    props.schema.forEach((question, index) => {
      formData[question.title] = newValues[`question_${index}`];
    });
    emit('update', formData);
  },
  { deep: true },
);
</script>

<template>
  <div class="space-y-4">
    <div v-for="(question, index) in schema" :key="index" class="space-y-2">
      <!-- Question Title -->
      <PText class="font-medium text-gray-90" variant="body">
        {{ question.title }}
      </PText>

      <!-- Text Input -->
      <VeeField
        v-if="question.type === 'text'"
        v-slot="{ value, handleChange }"
        :name="`question_${index}`"
        rules="required"
      >
        <Editor
          :model-value="value"
          :placeholder="t('feedback.writeResponse')"
          @update:model-value="handleChange"
        />
      </VeeField>

      <!-- Tag Selection -->
      <VeeField
        v-else-if="question.type === 'tag'"
        v-slot="{ value, handleChange, errorMessage }"
        :name="`question_${index}`"
        rules="required"
      >
        <div class="space-y-2">
          <div class="flex flex-wrap gap-2">
            <PChip
              v-for="option in question.options"
              :key="option.value"
              :color="value === option.value ? 'primary' : 'gray'"
              :label="option.title"
              size="small"
              :variant="value === option.value ? 'light' : 'pale'"
              class="cursor-pointer"
              @click="handleChange(option.value)"
            />
          </div>
          <PText v-if="errorMessage" class="text-danger" variant="caption2">
            {{ errorMessage }}
          </PText>
        </div>
      </VeeField>

      <!-- Select Dropdown -->
      <VeeField
        v-else-if="question.type === 'select'"
        v-slot="{ value, handleChange, errorMessage }"
        :name="`question_${index}`"
        rules="required"
      >
        <PListbox
          :model-value="value"
          :placeholder="t('feedback.selectOption')"
          :error="errorMessage"
          @update:model-value="handleChange"
        >
          <PListboxOption
            v-for="option in question.options"
            :key="option.value"
            :label="option.title"
            :value="option.value"
          />
        </PListbox>
      </VeeField>
    </div>
  </div>
</template>
