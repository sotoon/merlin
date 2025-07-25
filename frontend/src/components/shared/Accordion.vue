<template>
  <div class="rounded-lg border border-gray-20 bg-white shadow-sm">
    <!-- Accordion Header -->
    <button
      class="hover:bg-gray-5 flex w-full items-center justify-between p-4 text-left transition-colors"
      :class="{ 'border-b border-gray-20': isExpanded }"
      @click="toggle"
    >
      <div class="flex items-center gap-3">
        <slot name="icon" />
        <div>
          <slot name="title" />
        </div>
      </div>

      <!-- Expand/Collapse Icon -->
      <div class="flex items-center gap-2">
        <slot name="action-text" :is-expanded="isExpanded" />
        <i
          :class="[
            'text-gray-60 transition-transform duration-200',
            isExpanded ? 'i-mdi-chevron-up' : 'i-mdi-chevron-down',
          ]"
        />
      </div>
    </button>

    <!-- Accordion Content -->
    <div v-if="isExpanded" class="border-t border-gray-20 p-4">
      <slot name="content" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

interface Props {
  defaultExpanded?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  defaultExpanded: false,
});

const isExpanded = ref(props.defaultExpanded);

const toggle = () => {
  isExpanded.value = !isExpanded.value;
};

// Expose methods for parent components
defineExpose({
  expand: () => {
    isExpanded.value = true;
  },
  collapse: () => {
    isExpanded.value = false;
  },
  toggle,
  isExpanded: () => isExpanded.value,
});
</script>
