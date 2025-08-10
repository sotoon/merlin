<template>
  <div v-if="level" class="mb-6">
    <Accordion>
      <template #icon>
        <div
          class="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-white"
        >
          <PText class="font-bold" variant="body">
            {{ level.overall }}
          </PText>
        </div>
      </template>

      <template #title>
        <PText class="font-medium text-gray-90" variant="body">
          {{ t('timeline.currentLevel') }}
        </PText>
      </template>

      <template #action-text="{ isExpanded }">
        <PText class="text-gray-60" variant="caption1">
          {{
            isExpanded ? t('timeline.hideDetails') : t('timeline.showDetails')
          }}
        </PText>
      </template>

      <template #content>
        <div class="space-y-3">
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div
              v-for="[key, score] in Object.entries(level.details)"
              :key="key"
              class="bg-gray-5 flex items-center justify-between rounded-md px-3 py-2"
            >
              <PText class="text-gray-80" variant="caption1">
                {{ key }}
                <PChip
                  v-if="level.stages[key]"
                  size="small"
                  color="primary"
                  :label="level.stages[key]"
                />
              </PText>
              <div class="flex items-center gap-2">
                <div class="flex gap-1">
                  <div
                    v-for="i in level.max_level || 7"
                    :key="i"
                    class="h-2 w-2 rounded-full"
                    :class="i <= score ? 'bg-primary' : 'bg-gray-20'"
                  />
                </div>
                <PText class="font-medium text-gray-90" variant="caption1">
                  {{ score }}
                </PText>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Accordion>
  </div>
</template>

<script lang="ts" setup>
import { PText, PChip } from '@pey/core';
import Accordion from '~/components/shared/Accordion.vue';

interface LevelDetails {
  [key: string]: number;
}

interface LevelStages {
  [key: string]: string;
}

interface UserLevel {
  overall: number;
  details: LevelDetails;
  max_level?: number;
  stages: LevelStages;
}

defineProps<{
  level?: UserLevel;
}>();

const { t } = useI18n();
</script>
