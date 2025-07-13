<template>
  <form class="space-y-4" @submit="onSubmit">
    <VeeField v-slot="{ value, handleChange }" name="content">
      <Editor
        :model-value="value"
        :placeholder="t('note.writeCommentContent')"
        @update:model-value="handleChange"
      />
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
import { PButton } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

const props = defineProps<{
  comment?: Schema<'Comment'>;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [
    values: Schema<'CommentRequest'>,
    ctx: SubmissionContext<Schema<'CommentRequest'>>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<Schema<'CommentRequest'>>({
  initialValues: {
    content: props.comment?.content || '',
  },
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
