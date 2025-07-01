<script lang="ts" setup>
import { PText, PTooltip } from '@pey/core';

defineProps<{
  entry: Schema<'Feedback'>;
}>();

const { t } = useI18n();
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
        {{ t('common.content') }}
      </PText>
      <EditorContent class="text-gray-80" :content="entry.content" />
    </div>

    <div v-if="entry.evidence" class="mt-4 border-t border-gray-20 pt-4">
      <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
        {{ t('feedback.evidence') }}
      </PText>
      <EditorContent class="text-gray-80" :content="entry.evidence" />
    </div>
  </div>
</template>
