<script lang="ts" setup>
import { PText, PHeading } from '@pey/core';

defineProps<{
  entries: Schema<'Feedback'>[];
  formSchema?: FeedbackFormSchema;
}>();

const { t } = useI18n();
</script>

<template>
  <div class="mt-8">
    <PHeading :lvl="4" responsive>
      {{ t('feedback.entries') }}
    </PHeading>

    <div v-if="entries.length" class="mt-4 space-y-4">
      <FeedbackRequestEntryCard
        v-for="entry in entries"
        :key="entry.uuid"
        :entry="entry"
        :form-schema="formSchema"
      />
    </div>
    <PText v-else as="p" class="mt-4 text-center text-gray-80" responsive>
      {{ t('feedback.noEntries') }}
    </PText>
  </div>
</template>
