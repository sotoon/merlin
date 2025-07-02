<script setup lang="ts">
import { PText } from '@pey/core';
import { useRouter } from 'vue-router';

definePageMeta({ name: 'feedback-adhoc-new' });

const { t } = useI18n();
const router = useRouter();

const handleSuccess = () => {
  router.push({ name: 'feedback' });
};

const handleCancel = () => {
  router.back();
};
</script>

<template>
  <div>
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-comment-quote-outline text-h1 text-primary" />
      <PText as="h2" variant="h3" weight="bold">
        {{ t('feedback.createAdhocFeedback') }}
      </PText>
    </div>
    <FeedbackAdhocForm @success="handleSuccess" @cancel="handleCancel" />
  </div>
</template>
