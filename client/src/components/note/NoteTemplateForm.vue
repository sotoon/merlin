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

    <VeeField v-slot="{ componentField }" name="content" rules="required">
      <Editor v-bind="componentField" />
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
  note?: Note;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteFormValues];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteFormValues>({
  initialValues: {
    title: props.note?.title,
    content: props.note?.content,
  },
});

const onSubmit = handleSubmit((values) => {
  emit('submit', values);
});
</script>
