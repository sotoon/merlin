<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-00 p-4">
    <PBox class="container max-w-md bg-white p-5">
      <slot />
    </PBox>
  </div>
</template>

<script lang="ts" setup>
import { PBox } from '@pey/core';
</script>
