<template>
  <form class="space-y-4" @submit="onSubmit">
    <VeeField v-slot="{ componentField }" name="content">
      <PInput v-bind="componentField" hide-details :rows="8" type="textarea" />
    </VeeField>

    <div class="flex flex-wrap items-center justify-end gap-4 pt-8">
      <PButton
        class="shrink-0"
        color="gray"
        type="button"
        variant="light"
        @click="emit('cancel')"
      >
        {{ t('common.cancel') }}
      </PButton>

      <PButton
        class="shrink-0"
        :disabled="!meta.valid || !meta.dirty || isSubmitting"
        :loading="isSubmitting"
        type="submit"
        variant="fill"
      >
        {{ t('common.save') }}
      </PButton>
    </div>
  </form>
</template>

<script lang="ts" setup>
import { PButton, PInput } from '@pey/core';

const props = defineProps<{
  feedback?: NoteFeedback;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteFeedbackFormValues];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteFeedbackFormValues>({
  initialValues: {
    content: props.feedback?.content || '',
  },
});

const onSubmit = handleSubmit((values) => {
  emit('submit', values);
});
</script>
