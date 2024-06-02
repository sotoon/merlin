<template>
  <NuxtLink
    v-slot="slot"
    class="group"
    :external
    :target="external ? '_blank' : undefined"
    :to
  >
    <div
      class="relative flex items-center gap-3 rounded p-3"
      :class="{
        'bg-primary-10': slot?.isActive,
        'group-focus:bg-gray-00 hover:bg-gray-00': !slot?.isActive,
      }"
    >
      <i
        class="text-h4"
        :class="[
          icon,
          {
            'text-primary': slot?.isActive,
            'text-gray': !slot?.isActive,
          },
        ]"
      />

      <PText
        :class="{
          'text-gray-100': slot?.isActive,
          'text-gray-80': !slot?.isActive,
        }"
        :weight="slot?.isActive ? 'medium' : 'regular'"
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
  external?: boolean;
}

defineProps<SidebarLinkProps>();
</script>
