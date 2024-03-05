<template>
  <div class="flex min-h-screen items-center justify-center p-4">
    <PBox class="container max-w-md space-y-8 bg-white p-5">
      <PText as="h1" class="text-center" variant="h3">
        {{ t('login.title') }}
      </PText>

      <LoginForm />
    </PBox>
  </div>
</template>

<script lang="ts" setup>
import { PBox, PText } from '@pey/core';

definePageMeta({
  middleware: ['no-auth'],
});

const { t } = useI18n();
</script>
