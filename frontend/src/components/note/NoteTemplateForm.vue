<template>
  <form class="space-y-4" @submit="onSubmit">
    <VeeField
      v-slot="{ componentField }"
      :label="t('note.title')"
      name="title"
      rules="required"
    >
      <PInput
        class="grow"
        v-bind="componentField"
        hide-details
        :label="t('note.title')"
        required
      />
    </VeeField>

    <VeeField v-slot="{ value, handleChange }" name="content" rules="required">
      <Editor :model-value="value" @update:model-value="handleChange" />
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
import type { SubmissionContext } from 'vee-validate';

const props = defineProps<{
  note?: Note;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteFormValues, ctx: SubmissionContext<NoteFormValues>];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteTemplateFormValues>({
  initialValues: {
    title: props.note?.title || '',
    content: props.note?.content || '',
  },
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
