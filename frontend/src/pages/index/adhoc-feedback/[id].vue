<script setup lang="ts">
import { PBox, PTooltip, PText, PLoading } from '@pey/core';
import { useQueryClient } from '@tanstack/vue-query';

definePageMeta({ name: 'adhoc-feedback-detail' });

const route = useRoute();
const { t } = useI18n();
const queryClient = useQueryClient();

const {
  data: entry,
  isPending,
  error,
} = useGetAdhocFeedbackEntry(String(route.params.id));

const { data: forms } = useGetFeedbackForms();

const isStructuredResponse = computed(() => {
  if (!entry.value) return false;
  try {
    const parsed = JSON.parse(entry.value.content);
    return typeof parsed === 'object' && parsed !== null;
  } catch {
    return false;
  }
});

// Get the form schema if this is a structured response
const resolvedFormSchema = computed((): FeedbackFormSchema | undefined => {
  if (!isStructuredResponse.value || !forms.value || !entry.value)
    return undefined;

  // Use form_uuid to get the correct schema
  if (entry.value.form_uuid) {
    const form = forms.value.find((f) => f.uuid === entry.value.form_uuid);
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

watch(
  () => entry.value?.note,
  (newVal) => {
    if (newVal && !newVal.read_status) {
      const { execute } = useUpdateNoteReadStatus({ id: newVal.uuid });
      execute(true);
      queryClient.invalidateQueries({ queryKey: ['adhoc-feedback-entries'] });
    }
  },
  { once: true },
);
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <div class="px-2 sm:px-4">
      <div v-if="isPending" class="flex items-center justify-center py-8">
        <PLoading class="text-primary" :size="20" />
      </div>

      <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
        <PText as="p" class="text-center text-danger" responsive>
          {{ t('feedback.getError') }}
        </PText>
      </div>

      <div v-else-if="entry">
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
      </div>

      <div v-else class="flex flex-col items-center gap-4 py-8">
        <PText as="p" class="text-center text-gray-80" responsive>
          {{ t('feedback.feedbackNotFound') }}
        </PText>
      </div>
    </div>
  </PBox>
</template>
