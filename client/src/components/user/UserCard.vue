<template>
  <PCard
    :footer-border="false"
    :header-border="false"
    header-variant="primary-dark"
    :title="user.name"
  >
    <PText as="p" class="truncate text-gray-80" variant="caption1">
      {{ t('user.teamName', { name: user.team }) }}
    </PText>

    <template #footer>
      <div class="grow">
        <PText class="text-gray-50" variant="caption2">
          {{ user.email }}
        </PText>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PText } from '@pey/core';

defineProps<{ user: User }>();

const { t } = useI18n();
</script>
