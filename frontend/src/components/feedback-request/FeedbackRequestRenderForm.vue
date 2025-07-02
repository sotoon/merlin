<script setup lang="ts">
import { PText, PChip, PButton, PCheckboxGroup, PCheckbox } from '@pey/core';

const props = defineProps<{
  schema?: FeedbackFormSchema;
  responses?: Record<string, any>;
  isPreview?: boolean;
}>();

const { t } = useI18n();

// Check if this is a preview mode (showing form structure) or response mode (showing actual responses)
const isPreviewMode = computed(() => props.isPreview !== false);

// Helper function to get response value
const getResponseValue = (questionKey: string) => {
  return props.responses?.[questionKey];
};

// Defensive checks
const hasSchema = computed(() => {
  return (
    props.schema && props.schema.sections && props.schema.sections.length > 0
  );
});
</script>

<template>
  <div class="bg-gray-5 space-y-4 rounded-lg border border-gray-20 p-4">
    <div v-if="!hasSchema" class="text-center text-gray-60">
      <PText variant="caption2">{{ t('feedback.noFormSchema') }}</PText>
    </div>

    <div v-else-if="hasSchema" class="space-y-6">
      <div
        v-for="section in schema!.sections"
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
            <div
              v-if="question.type === 'text'"
              class="rounded border border-gray-20 bg-white p-3"
            >
              <!-- Preview Mode -->
              <PText
                v-if="isPreviewMode"
                class="text-gray-60"
                variant="caption2"
              >
                {{ question.placeholder || t('feedback.textResponse') }}
              </PText>

              <!-- Response Mode -->
              <EditorContent
                v-else
                :content="
                  getResponseValue(question.key) || t('feedback.noResponse')
                "
              />
            </div>

            <!-- Likert Scale -->
            <div v-else-if="question.type === 'likert'" class="space-y-2">
              <!-- Preview Mode -->
              <div
                v-if="isPreviewMode"
                class="flex items-center justify-between gap-4"
              >
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.min]
                }}</span>
                <div class="flex gap-2">
                  <PButton
                    v-for="i in (question.scale?.max || 5) -
                    (question.scale?.min || 1) +
                    1"
                    :key="i"
                    variant="outlined"
                    size="small"
                    disabled
                  >
                    {{ i }}
                  </PButton>
                </div>
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.max]
                }}</span>
              </div>

              <!-- Response Mode -->
              <div v-else class="flex items-center justify-between gap-4">
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.min]
                }}</span>
                <div class="flex gap-2">
                  <PButton
                    v-for="i in (question.scale?.max || 5) -
                    (question.scale?.min || 1) +
                    1"
                    :key="i"
                    :variant="
                      getResponseValue(question.key) === i ? 'fill' : 'outlined'
                    "
                    size="small"
                    disabled
                  >
                    {{ i }}
                  </PButton>
                </div>
                <span class="text-sm text-gray-60">{{
                  question.scale?.labels[question.scale?.max]
                }}</span>
              </div>
            </div>

            <!-- Tag Selection (Multiple) -->
            <div
              v-else-if="question.type === 'tag'"
              class="flex flex-wrap gap-2"
            >
              <!-- Preview Mode -->
              <template v-if="isPreviewMode">
                <PChip
                  v-for="option in question.options"
                  :key="option.value"
                  color="gray"
                  :label="option.label"
                  size="small"
                  variant="light"
                />
              </template>

              <!-- Response Mode -->
              <template v-else>
                <template v-if="getResponseValue(question.key)?.length">
                  <PChip
                    v-for="selectedValue in getResponseValue(question.key)"
                    :key="selectedValue"
                    color="primary"
                    :label="
                      question.options?.find(
                        (opt) => opt.value === selectedValue,
                      )?.label || selectedValue
                    "
                    size="small"
                    variant="light"
                  />
                </template>
                <PText v-else class="text-gray-60" variant="caption2">
                  {{ t('feedback.noResponse') }}
                </PText>
              </template>
            </div>

            <!-- Multiple Choice -->
            <div
              v-else-if="question.type === 'multiple_choice'"
              class="space-y-2"
            >
              <!-- Preview Mode -->
              <div v-if="isPreviewMode" class="space-y-2">
                <PCheckboxGroup :model-value="[]" flow="vertical" disabled>
                  <PCheckbox
                    v-for="option in question.options"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </PCheckbox>
                </PCheckboxGroup>
              </div>

              <!-- Response Mode -->
              <div v-else class="space-y-2">
                <template v-if="getResponseValue(question.key)?.length">
                  <PCheckboxGroup
                    :model-value="getResponseValue(question.key)"
                    flow="vertical"
                    disabled
                  >
                    <PCheckbox
                      v-for="option in question.options"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </PCheckbox>
                  </PCheckboxGroup>
                </template>
                <PText v-else class="text-gray-60" variant="caption2">
                  {{ t('feedback.noResponse') }}
                </PText>
              </div>
            </div>

            <!-- Sort/Drag and Drop -->
            <div v-else-if="question.type === 'sort'" class="space-y-2">
              <!-- Preview Mode -->
              <div v-if="isPreviewMode" class="space-y-2">
                <div
                  v-for="option in question.options"
                  :key="option.value"
                  class="flex items-center gap-3 rounded border border-gray-20 bg-white p-3"
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
                  <PText variant="body">{{ option.label }}</PText>
                </div>
              </div>

              <!-- Response Mode -->
              <div v-else class="space-y-2">
                <template v-if="getResponseValue(question.key)?.length">
                  <div
                    v-for="(value, index) in getResponseValue(question.key)"
                    :key="value"
                    class="flex items-center gap-3 rounded border border-gray-20 bg-white p-3"
                  >
                    <div class="flex-shrink-0 text-gray-40">
                      <span class="text-sm font-medium">{{ index + 1 }}</span>
                    </div>
                    <PText variant="body">
                      {{
                        question.options?.find((opt) => opt.value === value)
                          ?.label || value
                      }}
                    </PText>
                  </div>
                </template>
                <PText v-else class="text-gray-60" variant="caption2">
                  {{ t('feedback.noResponse') }}
                </PText>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
