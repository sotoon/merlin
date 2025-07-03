<script lang="ts" setup>
import { PCard, PText, PTooltip } from '@pey/core';

const { t } = useI18n();
const { data: profile } = useGetProfile();

const props = defineProps<{
  entry: Schema<'Feedback'>;
}>();

const isReceiver = computed(() => {
  return profile.value?.uuid === props.entry.receiver.uuid;
});

const feedbackMessage = computed(() => {
  if (isReceiver.value) {
    return t('feedback.receivedFeedbackFrom', {
      name: props.entry.sender.name,
    });
  } else {
    return t('feedback.sentFeedbackTo', { name: props.entry.receiver.name });
  }
});
</script>

<template>
  <NuxtLink
    :to="{
      name: 'adhoc-feedback-detail',
      params: { id: entry.uuid },
    }"
  >
    <PCard
      class="h-full cursor-pointer transition hover:shadow-lg"
      header-border
      :title="
        entry.sender.name + ' ' + t('feedback.to') + ' ' + entry.receiver.name
      "
    >
      <PText class="text-gray-80" variant="body">
        {{ feedbackMessage }}
      </PText>

      <template #footer>
        <div class="flex items-center justify-between">
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
      </template>
    </PCard>
  </NuxtLink>
</template>
