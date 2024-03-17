<template>
  <NuxtLink v-slot="{ isActive }" class="group" :to="to">
    <div
      class="flex items-center gap-3 rounded p-2"
      :class="{
        'bg-primary-10': isActive,
        'group-focus:bg-gray-00 hover:bg-gray-00': !isActive,
      }"
    >
      <PText variant="subtitle">
        {{ icon }}
      </PText>

      <PText
        :class="{ 'text-gray-100': isActive, 'text-gray-80': !isActive }"
        :weight="isActive ? 'medium' : 'regular'"
        variant="caption1"
      >
        {{ label }}
      </PText>
    </div>
  </NuxtLink>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

import type { SidebarLink } from '~/components/sidebar/SidebarLinks';

interface SidebarLinkProps extends SidebarLink {}

defineProps<SidebarLinkProps>();
</script>
