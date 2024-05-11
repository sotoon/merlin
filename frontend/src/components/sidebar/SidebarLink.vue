<template>
  <NuxtLink v-slot="{ isActive }" class="group" :to="to">
    <div
      class="relative flex items-center gap-3 rounded p-3"
      :class="{
        'bg-primary-10': isActive,
        'group-focus:bg-gray-00 hover:bg-gray-00': !isActive,
      }"
    >
      <i
        class="text-h4"
        :class="[
          icon,
          {
            'text-primary': isActive,
            'text-gray': !isActive,
          },
        ]"
      />

      <PText
        :class="{ 'text-gray-100': isActive, 'text-gray-80': !isActive }"
        :weight="isActive ? 'medium' : 'regular'"
        variant="caption1"
      >
        {{ label }}
      </PText>

      <Badge :count="badgeCount" />
    </div>
  </NuxtLink>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

import type { SidebarLink } from '~/components/sidebar/SidebarLinks';

interface SidebarLinkProps extends SidebarLink {
  badgeCount?: number;
}

defineProps<SidebarLinkProps>();
</script>
