<script setup lang="ts">
import { PBox, PText } from '@pey/core';
import { useRouter } from 'vue-router';

definePageMeta({ name: 'adhoc-feedback-new' });

const { t } = useI18n();
const router = useRouter();

const handleSuccess = () => {
  router.push({ name: 'adhoc-feedback' });
};

const handleCancel = () => {
  router.back();
};
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
