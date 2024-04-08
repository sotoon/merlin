<template>
  <tr>
    <th class="whitespace-nowrap py-3 pe-6 ps-2">
      <PText
        class="flex items-center text-gray-80"
        variant="caption1"
        weight="extraBold"
      >
        {{ label }}
      </PText>
    </th>

    <td class="w-full whitespace-nowrap px-6">
      <slot>
        <PText class="flex-grow text-gray-60" variant="caption1">
          {{ value || '-' }}
        </PText>
      </slot>
    </td>
  </tr>
</template>

<script lang="ts" setup>
import { PText } from '@pey/core';

interface PropertyTableRowProps {
  label?: string;
  value?: string | number | null;
}

defineProps<PropertyTableRowProps>();
</script>
