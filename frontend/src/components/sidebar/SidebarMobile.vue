<template>
  <button class="h-full" @click="sidebarOpen = true">
    <Icon name="mdi:chevron-double-left" />
  </button>

  <PSheet
    v-model="sidebarOpen"
    class="w-fit"
    body-class="px-0 py-0"
    side="right"
    @click="sidebarOpen = false"
  >
    <Sidebar />
  </PSheet>
</template>

<script lang="ts" setup>
import { PSheet } from '@pey/core';

const sidebarOpen = ref(false);
</script>
