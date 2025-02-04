<template>
  <div class="px-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <i
          class="i-mdi-form mb-3 me-4 inline-block align-middle text-h1 text-primary"
        />

        <PText responsive variant="title" weight="bold">
          {{ form.name }}
        </PText>
      </div>

      <PChip v-if="form.is_filled" color="success" :label="t('form.filled')" />
    </div>

    <div class="mt-4">
      <PText v-if="form.assigned_by" as="p" class="text-gray-60" variant="caption1">
        {{ t('form.evaluatee') }}: {{ form.assigned_by }}
      </PText>
    </div>

    <article class="mt-4 py-4">
      <EditorContent v-if="form.description" :content="form.description" />

      <hr class="my-8 border-gray-10" />

      <VeeForm
        v-slot="{ meta }"
        class="space-y-8 sm:space-y-12"
        :initial-values="form.previous_responses"
        @submit="handleSubmitForm"
      >
        <FormQuestion
          v-for="question in form.questions"
          :key="question.id"
          :question="question"
          :disabled="form.is_expired"
        />

        <div
          v-if="!form.is_expired && !form.is_filled"
          class="flex justify-end"
        >
          <PButton
            class="w-full sm:w-fit"
            color="primary"
            :disabled="!meta.valid || pending"
            :loading="pending"
            type="submit"
            variant="fill"
          >
            {{ t('common.submit') }}
          </PButton>
        </div>
      </VeeForm>
    </article>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PChip, PText } from '@pey/core';

const props = defineProps<{ form: FormDetails }>();

const { t } = useI18n();
const { execute: submitForm, pending } = useSubmitFormResponse(props.form.id);

// TODO: fix type
const handleSubmitForm = (values: any) => {
  console.log(values);
  submitForm({
    body: {
      responses: Object.entries(values).reduce((acc: any, [key, value]) => {
        acc[key] = value === 0 ? null : value;
        return acc;
      }, {}),
    },
    onSuccess: () => {
      navigateTo({ name: 'forms' });
    },
  });
};
</script>
