<script setup lang="ts">
import { PText, PChip } from '@pey/core';

const props = defineProps<{
  schema?: SchemaQuestion[];
  responses?: Record<string, any>;
  isPreview?: boolean;
}>();

const { t } = useI18n();

// Check if this is a preview mode (showing form structure) or response mode (showing actual responses)
const isPreviewMode = computed(() => props.isPreview !== false);
</script>

<template>
  <div class="bg-gray-5 space-y-4 rounded-lg border border-gray-20 p-4">
    <div v-if="!schema?.length" class="text-center text-gray-60">
      <PText variant="caption2">{{ t('feedback.noFormSchema') }}</PText>
    </div>

    <div v-else class="space-y-4">
      <div v-for="(question, index) in schema" :key="index" class="space-y-2">
        <!-- Question Title -->
        <PText class="font-medium text-gray-90" variant="body">
          {{ question.title }}
        </PText>

        <!-- Text Input -->
        <div
          v-if="question.type === 'text'"
          class="rounded border border-gray-20 bg-white p-3"
        >
          <!-- Preview Mode -->
          <PText v-if="isPreviewMode" class="text-gray-60" variant="caption2">
            {{ t('feedback.textResponse') }}
          </PText>

          <!-- Response Mode -->
          <EditorContent
            v-else
            :content="
              (responses && responses[question.title]) ||
              t('feedback.noResponse')
            "
          />
        </div>

        <!-- Tag Selection -->
        <div v-else-if="question.type === 'tag'" class="flex flex-wrap gap-2">
          <!-- Preview Mode -->
          <template v-if="isPreviewMode">
            <PChip
              v-for="option in question.options"
              :key="option.value"
              color="gray"
              :label="option.title"
              size="small"
              variant="light"
            />
          </template>

          <!-- Response Mode -->
          <template v-else>
            <PChip
              v-if="responses && responses[question.title]"
              color="primary"
              :label="
                question.options?.find(
                  (opt) =>
                    opt.value === (responses && responses[question.title]),
                )?.title ||
                (responses && responses[question.title])
              "
              size="small"
              variant="light"
            />
            <PText v-else class="text-gray-60" variant="caption2">
              {{ t('feedback.noResponse') }}
            </PText>
          </template>
        </div>

        <!-- Select Dropdown -->
        <div
          v-else-if="question.type === 'select'"
          class="rounded border border-gray-20 bg-white p-3"
        >
          <!-- Preview Mode -->
          <PText v-if="isPreviewMode" class="text-gray-60" variant="caption2">
            {{ question.options?.[0]?.title || t('feedback.selectOption') }}
          </PText>

          <!-- Response Mode -->
          <PText v-else class="text-gray-90" variant="body">
            {{
              question.options?.find(
                (opt) => opt.value === (responses && responses[question.title]),
              )?.title ||
              (responses && responses[question.title]) ||
              t('feedback.noResponse')
            }}
          </PText>
        </div>
      </div>
    </div>
  </div>
</template>
