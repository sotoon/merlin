<template>
  <PText as="p" weight="bold">
    {{ question.question_text }}
  </PText>

  <div v-if="avg != null && percentage != null" class="mt-8 lg:me-6">
    <div class="relative w-full">
      <div
        class="absolute mt-4 min-w-10 translate-x-1/2 rounded bg-white p-2 text-center shadow"
        :style="{
          right: `${percentage}%`,
        }"
      >
        <PText as="span" variant="subtitle" weight="bold">
          {{ avg.toLocaleString('fa-IR') }}
        </PText>
      </div>
    </div>

    <PLinearProgress :percentage="percentage" />

    <div class="mb-12 mt-2 flex w-full justify-between">
      <PText as="span" class="text-gray-60">
        {{ question.scale_min.toLocaleString('fa-IR') }}
      </PText>
      <PText as="span" class="text-gray-60">
        {{ question.scale_max.toLocaleString('fa-IR') }}
      </PText>
    </div>
  </div>

  <PText v-else as="p" class="mb-8 mt-4 italic text-gray-60">
    {{ t('form.noResults') }}
  </PText>
</template>

<script lang="ts" setup>
import { PLinearProgress, PText } from '@pey/core';

const props = defineProps<{
  question: Question;
  disabled?: boolean;
  avg?: number | null;
}>();

const { t } = useI18n();

const percentage = computed(() =>
  props.avg != null
    ? Math.min(
        Math.max(
          ((props.avg - props.question.scale_min) /
            (props.question.scale_max - props.question.scale_min)) *
            100,
          0,
        ),
        100,
      )
    : null,
);
</script>
