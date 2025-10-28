<script setup lang="ts">
import { PBox, PText, useToast } from '@pey/core';
import { useRouter } from 'vue-router';

definePageMeta({ name: 'adhoc-feedback-new' });

const { t } = useI18n();
const router = useRouter();
const toast = useToast();

function handleSuccess(data: Schema<'Feedback'> | Schema<'Feedback'>[]) {
  // Show success message
  const count = Array.isArray(data) ? data.length : 1;
  const message = count > 1 
    ? t('feedback.adhocFeedbacksSentSuccess', { count })
    : t('feedback.adhocFeedbackSentSuccess');
  
  toast.success({
    title: t('common.success'),
    message: message,
  });
  
  // Navigate to sent feedbacks page
  router.push({ name: 'adhoc-feedback', query: { tab: 'sent' } });
}

function handleCancel() {
  router.back();
}
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-comment-quote-outline text-h1 text-primary" />
      <PText as="h2" variant="h3" weight="bold">
        {{ t('feedback.createAdhocFeedback') }}
      </PText>
    </div>
    <FeedbackAdhocForm @success="handleSuccess" @cancel="handleCancel" />
  </PBox>
</template>
