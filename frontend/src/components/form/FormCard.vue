<template>
  <PCard
    class="transition-shadow duration-300 hover:shadow-lg"
    header-border
    :title="form.name"
  >
    <EditorContentPreview class="text-gray-80" :content="form.description" />

    <template #title>
      <PText as="h3" class="truncate" weight="medium">
        {{ form.name }}
      </PText>
    </template>

    <template #toolbar>
      <PChip v-if="form.is_filled" color="success" :label="t('form.filled')" />
    </template>

    <template #footer>
      <div
        class="mt-2 flex grow items-end justify-between gap-2 overflow-hidden"
      >
        <PText
          v-if="displayAssignedBy && form.assigned_by_name"
          as="p"
          class="text-gray-60"
          variant="caption2"
        >
          {{ t('form.evaluatee') }}: {{ form.assigned_by_name }}
        </PText>
      </div>
    </template>
  </PCard>
</template>

<script lang="ts" setup>
import { PCard, PChip, PText } from '@pey/core';

defineProps<{
  form: Form;
  displayAssignedBy?: boolean;
}>();

const { t } = useI18n();
</script>
