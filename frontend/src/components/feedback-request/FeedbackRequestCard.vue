<script lang="ts" setup>
import { PCard, PText, PTooltip, PChip } from '@pey/core';
import { PeyCircleTickOutlineIcon, PeyClockIcon } from '@pey/icons';

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
}>();
const { t } = useI18n();

const chipConfig = computed(() => {
  const submittedCount =
    props.request.requestees?.filter((r) => r.answered).length || 0;
  const totalCount = props.request.requestees?.length || 0;

  if (submittedCount === totalCount) {
    return {
      color: 'success' as const,
      icon: PeyCircleTickOutlineIcon,
      label: t('feedback.submitted'),
    };
  }

  return {
    color: 'warning' as const,
    icon: PeyClockIcon,
    label: `${submittedCount}/${totalCount} ${t('feedback.submitted')}`,
  };
});
</script>

<template>
  <NuxtLink
    :to="{
      name: 'feedback-request-detail',
      params: { requestId: request.uuid },
    }"
  >
    <PCard
      class="h-full cursor-pointer transition hover:shadow-lg"
      header-border
      :title="request.title"
    >
      <template #toolbar>
        <div class="flex items-center justify-end gap-1 sm:ms-4" @click.prevent>
          <PChip
            class="whitespace-nowrap"
            :color="chipConfig.color"
            :icon="chipConfig.icon"
            :label="chipConfig.label"
            size="small"
          />
        </div>
      </template>

      <EditorContentPreview class="text-gray-80" :content="request.content" />

      <template #footer>
        <div
          class="mt-2 flex grow items-end justify-between gap-2 overflow-hidden"
        >
          <div
            class="flex flex-col gap-2 overflow-hidden text-gray-50 sm:flex-row sm:items-center"
          >
            <PTooltip>
              <PText class="text-nowrap" variant="caption2">
                {{ formatTimeAgo(new Date(request.date_updated), 'fa-IR') }}
              </PText>

              <template #content>
                <PText variant="caption2">
                  {{ t('note.lastEdit') }}:
                  <PText dir="ltr" variant="caption1">
                    {{ new Date(request.date_updated).toLocaleString('fa-IR') }}
                  </PText>
                </PText>
              </template>
            </PTooltip>

            <PText class="truncate" variant="caption2">
              {{ request.owner_name }}
            </PText>
          </div>

          <div v-if="request.deadline">
            <PText
              class="text-nowrap text-gray-50"
              dir="ltr"
              variant="caption2"
            >
              {{ t('feedback.deadline') }}:
              {{ new Date(request.deadline).toLocaleDateString('fa-IR') }}
            </PText>
          </div>
        </div>
      </template>
    </PCard>
  </NuxtLink>
</template>
