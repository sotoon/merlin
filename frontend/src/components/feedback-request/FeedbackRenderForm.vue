<script setup lang="ts">
import { PInput, PText, PListbox, PListboxOption, PChip } from '@pey/core';

export interface FormQuestion {
  title: string;
  type: 'text' | 'tag' | 'select';
  options?: Array<{
    title: string;
    value: string;
  }>;
}

defineProps<{
  schema?: FormQuestion[];
}>();

const { t } = useI18n();
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
          <PText class="text-gray-60" variant="caption2">
            {{ t('feedback.textResponse') }}
          </PText>
        </div>

        <!-- Tag Selection -->
        <div v-else-if="question.type === 'tag'" class="flex flex-wrap gap-2">
          <PChip
            v-for="option in question.options"
            :key="option.value"
            color="gray"
            :label="option.title"
            size="small"
            variant="light"
          />
        </div>

        <!-- Select Dropdown -->
        <div
          v-else-if="question.type === 'select'"
          class="rounded border border-gray-20 bg-white p-3"
        >
          <PText class="text-gray-60" variant="caption2">
            {{ question.options?.[0]?.title || t('feedback.selectOption') }}
          </PText>
        </div>
      </div>
    </div>
  </div>
</template>
