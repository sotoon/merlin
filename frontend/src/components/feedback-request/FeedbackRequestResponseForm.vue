<script lang="ts" setup>
import { PButton, PLoading, PText } from '@pey/core';
import { useForm, Field as VeeField } from 'vee-validate';
import Editor from '~/components/shared/editor/Editor.vue';
import { useCreateFeedbackEntry } from '~/composables/useFeedbackServices';

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
}>();

const emit = defineEmits<{
  (e: 'success'): void;
}>();

const { t } = useI18n();
const { mutateAsync: createEntry, isPending } = useCreateFeedbackEntry(
  props.request.uuid,
);

const { handleSubmit, meta } = useForm<{ content: string; evidence: string }>({
  initialValues: {
    content: '',
    evidence: '',
  },
});

const onSubmit = handleSubmit((values) => {
  createEntry({
    ...values,
    feedback_request_uuid: props.request.uuid,
    receiver_id: props.request.owner_uuid,
  }).then(() => {
    emit('success');
  });
});
</script>

<template>
  <form
    class="mt-4 space-y-4 rounded-md border border-gray-20 p-4"
    @submit="onSubmit"
  >
    <div>
      <label id="feedback-content-label" class="mb-2 block">
        <PText class="cursor-default" variant="caption1" weight="bold">
          {{ t('feedback.writeFeedback') }}
          <span class="text-danger">*</span>
        </PText>
      </label>
      <VeeField
        v-slot="{ value, handleChange }"
        name="content"
        rules="required"
      >
        <Editor
          :model-value="value"
          :placeholder="t('feedback.writeFeedbackContent')"
          autofocus
          aria-labelledby="feedback-content-label"
          @update:model-value="handleChange"
        />
      </VeeField>
    </div>

    <div>
      <label id="feedback-evidence-label" class="mb-2 block">
        <PText class="cursor-default" variant="caption1" weight="bold">
          {{ t('feedback.evidence') }}
        </PText>
      </label>
      <VeeField v-slot="{ value, handleChange }" name="evidence">
        <Editor
          :model-value="value"
          :placeholder="t('feedback.writeEvidenceContent')"
          aria-labelledby="feedback-evidence-label"
          @update:model-value="handleChange"
        />
      </VeeField>
    </div>

    <div class="mt-4 flex items-center justify-end gap-4">
      <PLoading v-if="isPending" />
      <PButton type="submit" :disabled="isPending || !meta.valid">
        {{ t('common.submit') }}
      </PButton>
    </div>
  </form>
</template>
