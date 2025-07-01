<script lang="ts" setup>
import { PText } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'feedback-request-edit' });

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
}>();

const { t } = useI18n();

const { mutateAsync: updateRequest, isPending: isSubmitting } =
  useUpdateFeedbackRequest(props.request.uuid);

const handleSubmit = (
  values: Schema<'FeedbackRequestWrite'>,
  ctx: SubmissionContext<Schema<'FeedbackRequestWrite'>>,
) => {
  updateRequest(values).then(() => {
    navigateTo({
      name: 'feedback-request-detail',
      params: { requestId: props.request.uuid },
    });
    ctx.resetForm();
  });
};
</script>
<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-comment-quote-outline text-h1 text-primary" />
      <PText as="h2" variant="h3" weight="bold">
        {{ t('feedback.editTitle') }}
      </PText>
    </div>
    <FeedbackRequestForm
      :request="request"
      :is-submitting="isSubmitting"
      @submit="handleSubmit"
      @cancel="
        navigateTo({
          name: 'feedback-request-detail',
          params: { requestId: request.uuid },
        })
      "
    />
  </div>
</template>
