<template>
  <VeeField
    v-slot="{ componentField }"
    :name="`question_${question.id}`"
    rules="required"
  >
    <PRadioGroup
      class="[&>div]:flex-wrap"
      :disabled
      :label="question.question_text"
      v-bind="componentField"
      hide-details
      required
      variant="outlined"
    >
      <PRadio :value="0" class="sm:mt-4"> نمی‌دونم </PRadio>

      <PRadio
        v-for="i in question.scale_max - question.scale_min + 1"
        :key="i"
        :value="i"
        class="max-w-24 sm:mt-4"
      >
        {{ (i + question.scale_min - 1).toLocaleString('fa-IR') }}
      </PRadio>
    </PRadioGroup>
  </VeeField>
</template>

<script lang="ts" setup>
import { PRadio, PRadioGroup } from '@pey/core';

defineProps<{
  question: Question;
  disabled?: boolean;
}>();
</script>
