<script lang="ts" setup>
import { PText, PTooltip } from '@pey/core';

const props = defineProps<{
  entry: Schema<'Feedback'>;
  formSchema?: SchemaQuestion[];
}>();

const { t } = useI18n();
const { data: forms } = useGetFeedbackForms();

const isStructuredResponse = computed(() => {
  try {
    const parsed = JSON.parse(props.entry.content);
    return typeof parsed === 'object' && parsed !== null;
  } catch {
    return false;
  }
});

// Get the form schema if this is a structured response
const resolvedFormSchema = computed((): SchemaQuestion[] | undefined => {
  // If form schema is provided as prop, use it
  if (props.formSchema) return props.formSchema;

  // Otherwise, try to detect from available forms
  if (!isStructuredResponse.value || !forms.value) return undefined;

  // Try to find the form by checking if any form's schema matches the response structure
  for (const form of forms.value) {
    if (form.schema && Array.isArray(form.schema)) {
      const schemaQuestions = (form.schema as SchemaQuestion[]).map(
        (q) => q.title,
      );
      const responseKeys = Object.keys(JSON.parse(props.entry.content));

      // Check if all response keys match schema questions
      if (responseKeys.every((key) => schemaQuestions.includes(key))) {
        return form.schema as SchemaQuestion[];
      }
    }
  }

  return undefined;
});
</script>

<template>
  <div class="bg-gray-05 rounded-lg border border-gray-10 p-4">
    <div class="flex items-center justify-between">
      <PText variant="subtitle" weight="bold">
        {{ entry.sender.name }}
      </PText>
      <PTooltip>
        <PText class="text-nowrap" variant="caption2">
          {{ formatTimeAgo(new Date(entry.date_created), 'fa-IR') }}
        </PText>
        <template #content>
          <PText variant="caption2">
            {{ t('note.lastEdit') }}:
            <PText dir="ltr" variant="caption1">
              {{ new Date(entry.date_created).toLocaleString('fa-IR') }}
            </PText>
          </PText>
        </template>
      </PTooltip>
    </div>

    <div class="mt-4">
      <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
        {{ t('common.feedback') }}
      </PText>
      <FeedbackRequestRenderForm
        v-if="isStructuredResponse"
        :schema="resolvedFormSchema"
        :responses="
          isStructuredResponse ? JSON.parse(entry.content) : undefined
        "
      />
      <div v-else class="text-gray-80">
        <EditorContent :content="entry.content" />
      </div>
    </div>

    <div v-if="entry.evidence" class="mt-4 border-t border-gray-20 pt-4">
      <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
        {{ t('feedback.evidence') }}
      </PText>
      <EditorContent class="text-gray-80" :content="entry.evidence" />
    </div>
  </div>
</template>
