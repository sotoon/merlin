<script setup lang="ts">
import { PTooltip, PText } from '@pey/core';

definePageMeta({ name: 'adhoc-feedback-detail' });

const props = defineProps<{ entry: Schema<'Feedback'> }>();

const { t } = useI18n();

const { data: forms } = useGetFeedbackForms();

const isStructuredResponse = computed(() => {
  if (!props.entry) return false;
  try {
    const parsed = JSON.parse(props.entry.content);
    return typeof parsed === 'object' && parsed !== null;
  } catch {
    return false;
  }
});

// Get the form schema if this is a structured response
const resolvedFormSchema = computed((): FeedbackFormSchema | undefined => {
  if (!isStructuredResponse.value || !forms.value || !props.entry)
    return undefined;

  // Use form_uuid to get the correct schema
  if (props.entry.form_uuid) {
    const form = forms.value.find((f) => f.uuid === props.entry.form_uuid);
    if (
      form?.schema &&
      typeof form.schema === 'object' &&
      'sections' in form.schema
    ) {
      return form.schema as FeedbackFormSchema;
    }
  }

  return undefined;
});
</script>

<template>
  <div class="px-2 sm:px-4">
    <div>
      <!-- Header -->
      <div class="flex items-start justify-between gap-8">
        <div>
          <i
            class="i-mdi-comment-quote-outline mb-3 me-4 inline-block align-middle text-h1 text-primary"
          />
          <PText responsive variant="h1" weight="bold">
            {{ t('feedback.adhocFeedback') }}
          </PText>
        </div>
      </div>

      <!-- Metadata -->
      <div class="mt-6 flex flex-wrap items-center gap-4">
        <PText as="p" class="text-gray-50" variant="caption1">
          {{ t('common.date') }}:
          <PTooltip>
            <PText class="text-gray-70" variant="caption1">
              {{ formatTimeAgo(new Date(entry.date_created), 'fa-IR') }}
            </PText>
            <template #content>
              <PText dir="ltr" variant="caption1">
                {{ new Date(entry.date_created).toLocaleString('fa-IR') }}
              </PText>
            </template>
          </PTooltip>
        </PText>

        <PText as="p" class="text-gray-50" variant="caption1">
          {{ t('feedback.from') }}:
          <span class="text-primary">
            {{ entry.sender.name }}
          </span>
        </PText>

        <PText as="p" class="text-gray-50" variant="caption1">
          {{ t('feedback.to') }}:
          <span class="text-primary">
            {{ entry.receiver.name }}
          </span>
        </PText>
      </div>

      <!-- Content -->
      <article class="mt-4 py-4">
        <FeedbackRenderForm
          v-if="isStructuredResponse"
          class="border-none !p-0"
          :schema="resolvedFormSchema"
          :responses="JSON.parse(entry.content)"
        />
        <div v-else class="text-gray-80">
          <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
            {{ t('common.feedback') }}
          </PText>
          <EditorContent :content="entry.content" />
        </div>
      </article>

      <!-- Evidence -->
      <article v-if="entry.evidence" class="mt-4 py-4">
        <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
          {{ t('feedback.evidence') }}
        </PText>
        <div class="bg-gray-05 rounded-md border border-gray-20 p-4">
          <EditorContent class="text-gray-80" :content="entry.evidence" />
        </div>
      </article>

      <div class="mt-8">
        <NoteComments :note="entry.note" type="adhoc" />
      </div>
    </div>
  </div>
</template>
