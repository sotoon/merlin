<template>
  <NuxtLink v-slot="{ isActive }" class="group" to="/profile">
    <div
      class="flex items-center gap-2 overflow-hidden rounded p-2"
      :class="{
        'bg-primary-10': isActive,
        'group-focus:bg-gray-00 hover:bg-gray-00': !isActive,
      }"
    >
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary-20"
      >
        <PeyUserIcon class="text-primary" :size="20" />
      </div>

      <PText
        v-if="data"
        :class="{ 'text-gray-100': isActive, 'text-gray-80': !isActive }"
        :weight="isActive ? 'bold' : 'medium'"
        variant="caption1"
      >
        {{ data?.name }}
      </PText>

      <PLoading v-else-if="isPending" class="text-primary" />
    </div>
  </NuxtLink>
</template>

<script lang="ts" setup>
import { PLoading, PText } from '@pey/core';
import { PeyUserIcon } from '@pey/icons';

const { data, isPending } = useGetProfile();
</script>
