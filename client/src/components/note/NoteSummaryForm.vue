<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.writeSummaryFor', { title: note.title }) }}
    </PHeading>

    <form class="space-y-4" @submit="onSubmit">
      <VeeField v-slot="{ componentField }" name="summary">
        <PInput
          v-bind="componentField"
          hide-details
          :rows="8"
          type="textarea"
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
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PInput } from '@pey/core';

const props = defineProps<{
  note: Note;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteSummaryFormValues];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<NoteSummaryFormValues>({
  initialValues: {
    summary: props.note?.summary || '',
  },
});

const onSubmit = handleSubmit((values) => {
  emit('submit', values);
});
</script>
