<script lang="ts" setup>
import { PText, PHeading } from '@pey/core';
import FeedbackEntryCard from '~/components/feedback-request/FeedbackEntryCard.vue';

defineProps<{
  entries: Schema<'Feedback'>[];
}>();

const { t } = useI18n();
</script>

<template>
  <div class="mt-8">
    <PHeading :lvl="4" responsive>
      {{ t('feedback.entries') }}
    </PHeading>

    <div v-if="entries.length" class="mt-4 space-y-4">
      <FeedbackEntryCard
        v-for="entry in entries"
        :key="entry.uuid"
        :entry="entry"
      />
    </div>
    <PText v-else as="p" class="mt-4 text-center text-gray-80" responsive>
      {{ t('feedback.noEntries') }}
    </PText>
  </div>
</template>
