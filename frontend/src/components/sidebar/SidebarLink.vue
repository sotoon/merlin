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
        'bg-primary-10': isActiveProp ?? slot?.isActive,
        'group-focus:bg-gray-00 hover:bg-gray-00': !(
          isActiveProp ?? slot?.isActive
        ),
      }"
    >
      <i
        class="text-h4"
        :class="[
          icon,
          {
            'text-primary': isActiveProp ?? slot?.isActive,
            'text-gray': !(isActiveProp ?? slot?.isActive),
          },
        ]"
      />

      <PText
        :class="{
          'text-gray-100': isActiveProp ?? slot?.isActive,
          'text-gray-80': !(isActiveProp ?? slot?.isActive),
        }"
        :weight="isActiveProp ?? slot?.isActive ? 'medium' : 'regular'"
        variant="caption1"
      >
        {{ label }}
      </PText>

      <Badge class="absolute left-4" :count="badgeCount" :max="999" />
    </div>
  </NuxtLink>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';
import type { RouteLocationRaw } from 'vue-router';

export interface SidebarLink {
  icon: string;
  label: string;
  to: RouteLocationRaw;
}
interface SidebarLinkProps extends SidebarLink {
  badgeCount?: number;
  external?: boolean;
  isActive?: boolean;
}

const props = defineProps<SidebarLinkProps>();

const isActiveProp = computed(() => props.isActive);
</script>
