<template>
  <button class="h-full" @click="sidebarOpen = true">
    <i class="i-mdi-chevron-double-left text-h3" />
  </button>

  <PSheet
    v-model="sidebarOpen"
    class="w-fit"
    body-class="px-0 py-0"
    side="right"
  >
    <Sidebar />
  </PSheet>
</template>

<script lang="ts" setup>
import { PSheet } from '@pey/core';

const sidebarOpen = ref(false);
</script>
