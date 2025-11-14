<script lang="ts" setup>
import { PText, PButton } from '@pey/core';
import { SIDEBAR_TOUR_STEPS } from '~/constants/sidebarGuide';

interface Props {
  title: string;
  hasBadge?: boolean;
  isActive?: boolean;
  guideKey?: string;
}

const props = defineProps<Props>();

const isCollapsed = ref(true);
const contentRef = ref<HTMLElement>();
const contentHeight = ref(0);

const { start: startTour } = useIntro(
  SIDEBAR_TOUR_STEPS[props.guideKey || ''] || [],
  `sidebar-guide-${props.guideKey}`,
);

const updateContentHeight = () => {
  if (contentRef.value) {
    contentHeight.value = contentRef.value.scrollHeight + 8;
  }
};

watch(
  () => props.isActive,
  (newValue) => {
    if (newValue && isCollapsed.value) {
      isCollapsed.value = false;
    }
  },
  { immediate: true },
);

watch(isCollapsed, (newVal) => {
  if (!newVal) {
    startTour();
  }
});

onMounted(updateContentHeight);
onUpdated(updateContentHeight);
</script>

<template>
  <div>
    <PButton
      variant="ghost"
      color="gray"
      class="w-full items-center justify-between"
      @click="isCollapsed = !isCollapsed"
    >
      <PText as="h2" variant="subtitle" class="flex items-center gap-2">
        {{ title }}
      </PText>

      <div class="flex items-center gap-2">
        <div v-if="hasBadge" class="h-2 w-2 rounded-lg bg-danger" />
        <i
          class="text-h5 text-gray-60 transition-transform"
          :class="['i-mdi-chevron-down', { 'rotate-180': !isCollapsed }]"
        />
      </div>
    </PButton>

    <div
      class="overflow-hidden transition-all duration-200"
      :style="{ height: isCollapsed ? '0' : contentHeight + 'px' }"
    >
      <ul ref="contentRef" class="relative space-y-1 ps-3 pt-2">
        <div
          class="absolute right-2 top-2 h-[calc(100%-0.5rem)] w-px bg-gray-20"
        />
        <slot />
      </ul>
    </div>
  </div>
</template>
