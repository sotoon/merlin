<script setup lang="ts">
import { PBox, PText } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';
import { useCreateFeedbackRequest } from '~/composables/services/useFeedbackServices';

definePageMeta({ name: 'feedback-new' });

const { t } = useI18n();
const router = useRouter();
const { mutateAsync: createFeedbackRequest, isPending } =
  useCreateFeedbackRequest();

function handleSubmit(
  values: Schema<'FeedbackRequestWriteRequest'>,
  ctx: SubmissionContext<Schema<'FeedbackRequestWriteRequest'>>,
) {
  createFeedbackRequest({
    title: values.title,
    content: values.content,
    requestee_emails: values.requestee_emails,
    mentioned_users: values.mentioned_users,
    deadline: values.deadline,
    form_uuid: values.form_uuid,
  }).then((data) => {
    ctx.resetForm();
    router.push({ name: 'feedback-detail', params: { requestId: data.uuid } });
  });
}

function handleCancel() {
  router.back();
}
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-comment-quote-outline text-h1 text-primary" />
      <PText as="h2" variant="h3" weight="bold">
        {{ t('feedback.createTitle') }}
      </PText>
    </div>
    <FeedbackForm
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>
