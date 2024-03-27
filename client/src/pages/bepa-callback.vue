<template>
  <div class="flex flex-wrap items-center justify-center gap-4 py-4">
    <PLoading class="text-primary" :size="16" />
    <PText as="h1" class="text-center" variant="h4">
      {{ t('login.connectingToBepa') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PLoading, PText, useToast } from '@pey/core';

definePageMeta({
  layout: 'auth',
  middleware: ['no-auth'],
});

const { t } = useI18n();
const {
  query: { code, state },
} = useRoute();
const toast = useToast();
const { execute: handleBepaCallback } = useBepaCallback();

onMounted(() => {
  const storedStateValue = sessionStorage.getItem('stateValue');

  if (!state || storedStateValue !== state || typeof code !== 'string') {
    toast.error({ title: t('login.connectingToBepaFailed'), message: '' });
    navigateTo({ name: 'login', replace: true });

    return;
  }

  handleBepaCallback({
    query: { code },
    onSuccess: () => {
      navigateTo({ name: 'home', replace: true });
    },
    onError: () => {
      navigateTo({ name: 'login', replace: true });
    },
  });
});
</script>
