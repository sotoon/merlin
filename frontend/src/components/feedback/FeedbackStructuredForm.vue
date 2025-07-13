<script setup lang="ts">
import { PText, PChip, PButton, PCheckboxGroup, PCheckbox } from '@pey/core';
import { useForm } from 'vee-validate';
import draggable from 'vuedraggable';

const props = defineProps<{
  schema: FeedbackFormSchema;
  draftAnswers?: string;
}>();

const emit = defineEmits<{
  (e: 'update', value: Record<string, any>): void;
}>();

const { t } = useI18n();

// Create dynamic form fields based on schema
const formFields = computed(() => {
  const fields: Record<string, any> = {};
  props.schema.sections.forEach((section) => {
    section.items.forEach((question) => {
      if (question.default !== undefined) {
        fields[question.key] = question.default;
      } else if (question.type === 'multiple_choice' && question.default) {
        fields[question.key] = question.default;
      } else if (question.type === 'sort' && question.defaultOrder) {
        fields[question.key] = [...question.defaultOrder];
      } else if (question.type === 'tag') {
        fields[question.key] = [];
      } else {
        fields[question.key] = '';
      }
    });
  });
  return fields;
});

// Initialize form with proper initial values
const { values, setValues, setFieldValue } = useForm({
  initialValues: formFields.value,
});

// Watch for changes and emit the form data
watch(
  values,
  (newValues) => {
    emit('update', newValues);
  },
  { deep: true },
);

// Ensure form is properly initialized with the computed form fields
watch(
  formFields,
  (newFormFields) => {
    setValues(newFormFields);
  },
  { immediate: true },
);
watch(
  () => props.draftAnswers,
  (newAnswers) => {
    if (!newAnswers) return;
    try {
      const parsedAnswer = JSON.parse(newAnswers);
      setValues(parsedAnswer);
    } catch {
      /* empty */
    }
  },
  { immediate: true },
);

// Computed property for sortable items
const sortableItems = computed(() => {
  const items: Record<string, any[]> = {};

  if (!values) {
    return items;
  }

  // Process all sort questions
  props.schema.sections.forEach((section) => {
    section.items.forEach((question) => {
      if (question.type === 'sort' && question.key) {
        // Get the current order from form values
        const currentOrder = values[question.key] || [];

        // Map to draggable format
        items[question.key] = currentOrder.map((value: any) => {
          const option = question.options?.find((opt) => opt.value === value);
          const label = option?.label || value;
          return { value, label };
        });
      }
    });
  });

  return items;
});

// Update form state when items are dragged
const updateSortableItemsForQuestion = (
  questionKey: string,
  newItems: any[],
) => {
  if (!questionKey) return;
  const newValues = newItems.map((item: any) => item.value);
  setFieldValue(questionKey, newValues);
};
</script>

<template>
  <div class="space-y-6">
    <div
      v-for="section in schema.sections"
      :key="section.key"
      class="space-y-4"
    >
      <!-- Section Title -->
      <div class="border-b border-gray-20 pb-2">
        <PText class="font-bold text-gray-90" variant="h4">
          {{ section.title }}
        </PText>
      </div>

      <!-- Questions in Section -->
      <div class="space-y-4">
        <div
          v-for="question in section.items"
          :key="question.key"
          class="space-y-3"
        >
          <!-- Question Title and Required Indicator -->
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <PText class="font-medium text-gray-90" variant="body">
                {{ question.title }}
              </PText>
              <span
                v-if="question.required"
                class="select-none text-danger"
                title="Required field"
                >*</span
              >
            </div>

            <!-- Help Text -->
            <PText
              v-if="question.helpText"
              class="leading-relaxed text-gray-60"
              variant="caption2"
            >
              {{ question.helpText }}
            </PText>
          </div>

          <!-- Text Input -->
          <VeeField
            v-if="question.type === 'text'"
            v-slot="{ value, handleChange, errorMessage }"
            :name="question.key"
            :rules="question.required ? 'required' : ''"
          >
            <div class="space-y-1">
              <Editor
                :model-value="value"
                :placeholder="
                  question.placeholder || t('feedback.writeResponse')
                "
                @update:model-value="handleChange"
              />
              <PText v-if="errorMessage" class="text-danger" variant="caption2">
                {{ errorMessage }}
              </PText>
            </div>
          </VeeField>

          <!-- Likert Scale -->
          <VeeField
            v-else-if="question.type === 'likert'"
            v-slot="{ value, handleChange, errorMessage }"
            :name="question.key"
            :rules="question.required ? 'required' : ''"
          >
            <div class="space-y-2">
              <div class="flex items-center justify-between gap-4">
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.min]
                }}</span>
                <div class="flex gap-2">
                  <PButton
                    v-for="i in (question.scale?.max || 5) -
                    (question.scale?.min || 1) +
                    1"
                    :key="i"
                    :variant="value === i ? 'fill' : 'outlined'"
                    size="small"
                    type="button"
                    @click="handleChange(i)"
                  >
                    {{ i }}
                  </PButton>
                </div>
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.max]
                }}</span>
              </div>
              <PText v-if="errorMessage" class="text-danger" variant="caption2">
                {{ errorMessage }}
              </PText>
            </div>
          </VeeField>

          <!-- Tag Selection (Multiple) -->
          <VeeField
            v-else-if="question.type === 'tag'"
            v-slot="{ value, handleChange, errorMessage }"
            :name="question.key"
            :rules="question.required ? 'required' : ''"
          >
            <div class="space-y-2">
              <div class="flex flex-wrap gap-2">
                <PChip
                  v-for="option in question.options"
                  :key="option.value"
                  :color="value?.includes(option.value) ? 'primary' : 'gray'"
                  :label="option.label"
                  size="small"
                  :variant="value?.includes(option.value) ? 'light' : 'pale'"
                  class="cursor-pointer"
                  @click="
                    () => {
                      const currentValue = value || [];
                      const newValue = currentValue.includes(option.value)
                        ? currentValue.filter((v: any) => v !== option.value)
                        : [...currentValue, option.value];
                      handleChange(newValue);
                    }
                  "
                />
              </div>
              <PText v-if="errorMessage" class="text-danger" variant="caption2">
                {{ errorMessage }}
              </PText>
            </div>
          </VeeField>

          <!-- Multiple Choice -->
          <VeeField
            v-else-if="question.type === 'multiple_choice'"
            v-slot="{ value, handleChange, errorMessage }"
            :name="question.key"
            :rules="question.required ? 'required' : ''"
          >
            <div class="space-y-2">
              <PCheckboxGroup
                :model-value="value || []"
                flow="vertical"
                @update:model-value="handleChange"
              >
                <PCheckbox
                  v-for="option in question.options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </PCheckbox>
              </PCheckboxGroup>
              <PText v-if="errorMessage" class="text-danger" variant="caption2">
                {{ errorMessage }}
              </PText>
            </div>
          </VeeField>

          <!-- Sort/Drag and Drop -->
          <div v-else-if="question.type === 'sort'" class="space-y-2">
            <draggable
              v-model="sortableItems[question.key]"
              :group="{ name: question.key }"
              item-key="value"
              class="space-y-2"
              @end="
                updateSortableItemsForQuestion(
                  question.key,
                  sortableItems[question.key],
                )
              "
            >
              <template #item="{ element }">
                <div
                  class="hover:bg-gray-5 flex cursor-move items-center gap-3 rounded border border-gray-20 bg-white p-3"
                >
                  <div class="flex-shrink-0 text-gray-40">
                    <svg
                      class="h-5 w-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        d="M7 2a2 2 0 1 1 .001 4.001A2 2 0 0 1 7 2zm0 6a2 2 0 1 1 .001 4.001A2 2 0 0 1 7 8zm0 6a2 2 0 1 1 .001 4.001A2 2 0 0 1 7 14zm6-8a2 2 0 1 1-.001-4.001A2 2 0 0 1 13 6zm0 2a2 2 0 1 1 .001 4.001A2 2 0 0 1 13 8zm0 6a2 2 0 1 1 .001 4.001A2 2 0 0 1 13 14z"
                      />
                    </svg>
                  </div>
                  <PText variant="body">{{ element.label }}</PText>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sortable-ghost {
  opacity: 0.5;
  background: #f3f4f6;
}

.sortable-chosen {
  background: #e5e7eb;
}

.sortable-drag {
  background: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
</style>
