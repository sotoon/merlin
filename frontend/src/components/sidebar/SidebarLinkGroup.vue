<template>
  <div>
    <PText as="h1" class="py-1" variant="subtitle">
      {{ title }}
    </PText>

    <hr class="border-gray-10" />

    <ul class="mt-2 space-y-0.5">
      <li v-for="link in links" :key="link.label">
        <SidebarLink v-bind="link" />
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

import type { SidebarLinkGroup } from '~/components/sidebar/SidebarLinks';

interface SidebarLinkGroupProps extends SidebarLinkGroup {}

defineProps<SidebarLinkGroupProps>();
</script>
