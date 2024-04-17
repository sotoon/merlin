<template>
  <PScrollbar class="space-y-4 p-3">
    <PText v-if="title" as="h3" class="sticky start-0" weight="bold">
      {{ title }}
    </PText>

    <table>
      <tbody>
        <slot />
      </tbody>
    </table>
  </PScrollbar>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';

interface PropertyTableProps {
  title?: string;
}

defineProps<PropertyTableProps>();
</script>
