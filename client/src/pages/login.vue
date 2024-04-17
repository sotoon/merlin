<template>
  <div class="space-y-8">
    <PText as="h1" class="text-center" variant="h3">
      {{ t('login.title') }}
    </PText>

    <div class="space-y-4">
      <PButton
        class="w-full"
        color="secondary"
        :icon-start="PeyIAMIcon"
        size="large"
        type="button"
        variant="fill"
        @click="handleBepaLogin"
      >
        {{ t('login.bepaLogin') }}
      </PButton>

      <hr class="border-gray-10" />

      <LoginForm />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PText } from '@pey/core';
import { PeyIAMIcon } from '@pey/icons';

definePageMeta({
  name: 'login',
  layout: 'auth',
  middleware: ['no-auth'],
});

const { t } = useI18n();
const handleBepaLogin = useBepaLogin();
</script>
