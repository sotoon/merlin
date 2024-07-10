<template>
  <form v-if="visible" class="space-y-4" @submit="onSubmit">
    <VeeField v-slot="{ value, handleChange }" name="content">
      <Editor
        :model-value="value"
        :placeholder="t('note.writeMessageContent')"
        @update:model-value="handleChange"
      />
    </VeeField>

    <div class="flex flex-wrap items-center justify-end gap-4">
      <PButton
        class="shrink-0"
        color="gray"
        type="button"
        variant="light"
        @click="onCancel"
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
import { PButton } from '@pey/core';

const props = defineProps<{
  note: Note;
  feedback?: NoteFeedback;
}>();
const visible = defineModel<boolean>('visible');

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteFeedbackFormValues>({
  initialValues: {
    content: props.feedback?.content || '',
  },
  keepValuesOnUnmount: true,
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });
const { execute: createNoteFeedback, pending: isSubmitting } =
  useCreateNoteFeedback({ noteId: props.note.uuid });

const onSubmit = handleSubmit((values, ctx) => {
  createNoteFeedback({
    body: values,
    onSuccess: () => {
      ctx.resetForm();
      visible.value = false;
    },
  });
});

const onCancel = () => {
  visible.value = false;
};
</script>
