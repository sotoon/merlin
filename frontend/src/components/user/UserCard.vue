<template>
  <PCard
    class="transition-shadow duration-300 hover:shadow-lg"
    header-border
    :title="user.name || ''"
  >
    <PText as="p" class="truncate text-gray-80" variant="caption1">
      {{ t('user.teamName', { name: user.team }) }}
    </PText>

    <template #footer>
      <div dir="ltr" class="grow truncate">
        <PText class="text-gray-50" variant="caption2">
          {{ user.email }}
        </PText>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PText } from '@pey/core';

defineProps<{ user: Schema<'Profile'> | Schema<'ProfileList'> }>();

const { t } = useI18n();
</script>
