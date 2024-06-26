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
      <Editor
        :model-value="value"
        :placeholder="t('note.writeTemplateContent')"
        @update:model-value="handleChange"
      />
    </VeeField>

    <VeeField v-slot="{ componentField }" name="mentioned_users">
      <UserSelect v-bind="componentField" :label="t('note.share')" multiple />
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
  submit: [
    values: NoteTemplateFormValues,
    ctx: SubmissionContext<NoteTemplateFormValues>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const {
  meta,
  values: formValues,
  handleSubmit,
  setValues,
} = useForm<NoteTemplateFormValues>({
  initialValues: {
    title: props.note?.title || '',
    content: props.note?.content || '',
    mentioned_users: props.note?.mentioned_users || [],
  },
});

const isEditing = computed(() => Boolean(props.note));

useUnsavedChangesGuard({
  disabled: () => !isEditing.value || !meta.value.dirty,
});
useStoreDraft({
  disabled: isEditing,
  storageKey: 'note:draft:Template',
  values: computed(() => ({
    title: formValues.title,
    content: formValues.content,
  })),
  setValues: (values) =>
    setValues({
      ...formValues,
      title: values.title,
      content: values.content,
    }),
});

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
