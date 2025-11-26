<script lang="ts" setup>
import { PText, PButton } from '@pey/core';
import { SIDEBAR_TOUR_STEPS } from '~/constants/sidebarGuide';

interface Props {
  title: string;
  hasBadge?: boolean;
  isActive?: boolean;
  guideKey?: string;
  guideConditions?: Record<string, boolean>;
  id?: string;
}

const props = defineProps<Props>();

const registerCloseGroup = inject<
  ((id: string, closeFn: () => void) => void) | undefined
>('registerCloseGroup', undefined);
const closeAllGroupsExcept = inject<((id: string) => void) | undefined>(
  'closeAllGroupsExcept',
  undefined,
);

const isCollapsed = ref(true);
const contentRef = ref<HTMLElement>();
const contentHeight = ref(0);

if (props.id && registerCloseGroup) {
  registerCloseGroup(props.id, () => {
    isCollapsed.value = true;
  });
}

const tourSteps = computed(() => {
  const allSteps = SIDEBAR_TOUR_STEPS[props.guideKey || ''] || [];

  const filteredSteps = props.guideConditions
    ? allSteps.filter(
        (step) => !step.visibility || props.guideConditions?.[step.visibility],
      )
    : allSteps;

  return filteredSteps.map((step, index) => ({ ...step, step: index + 1 }));
});

const { start: startTour } = useIntro(
  tourSteps,
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
    if (
      props.guideKey &&
      !localStorage.getItem(`sidebar-guide-${props.guideKey}`) &&
      props.id &&
      closeAllGroupsExcept
    ) {
      closeAllGroupsExcept(props.id);
    }

    setTimeout(() => {
      startTour();
    }, 300);
  }
});

onMounted(updateContentHeight);
onUpdated(updateContentHeight);
</script>

<template>
  <div>
    <PButton
      :id="id"
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
