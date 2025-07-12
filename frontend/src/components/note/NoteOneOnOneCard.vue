<script lang="ts" setup>
import { PCard, PText, PChip } from '@pey/core';

const props = defineProps<{
  oneOnOne: Schema<'OneOnOne'>;
  username: string;
}>();

const { t } = useI18n();

const isTeamLeader = computed(() => props.oneOnOne.leader_vibe);
</script>

<template>
  <PCard
    class="transition-shadow duration-300 hover:shadow-lg"
    header-border
    :title="oneOnOne.actions || ''"
  >
    <div class="space-y-4">
      <div class="space-y-2">
        <PText weight="medium">{{ t('oneOnOne.performanceManagement') }}</PText>
        <EditorContentPreview
          class="text-gray-80"
          :content="oneOnOne.performance_summary"
        />
      </div>
    </div>

    <template #title>
      <PText as="h3" class="truncate" weight="medium">
        {{ oneOnOne.note.title }}
      </PText>
    </template>

    <template #icon>
      <i class="i-mdi-account-supervisor block text-h3 text-gray" />
    </template>

    <template #toolbar>
      <div class="flex items-center justify-end gap-2 sm:ms-4">
        <PChip
          v-if="isTeamLeader"
          :color="
            oneOnOne.leader_vibe === ':)'
              ? 'success'
              : oneOnOne.leader_vibe === ':('
                ? 'danger'
                : 'warning'
          "
          :label="getVibeEmoji(oneOnOne.leader_vibe)"
        />
        <PChip
          v-if="!isTeamLeader"
          :color="
            oneOnOne.member_vibe === ':)'
              ? 'success'
              : oneOnOne.member_vibe === ':('
                ? 'danger'
                : 'warning'
          "
          :label="`${getVibeEmoji(oneOnOne.member_vibe) || 'بازخوردی ثبت نشده است'}`"
        />
      </div>
    </template>

    <template #footer>
      <div
        class="mt-2 flex grow items-end justify-between gap-2 overflow-hidden"
      >
        <PText class="text-nowrap" variant="caption2">
          {{ formatTimeAgo(new Date(oneOnOne.date_updated || ''), 'fa-IR') }}
        </PText>
      </div>
    </template>
  </PCard>
</template>
