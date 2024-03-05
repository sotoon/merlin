<template>
  <div class="container">
    <p class="text-center text-lg text-primary">
      {{ t('common.appName') }}
    </p>

    <div class="flex flex-col items-center">
      <PLoading v-if="pending" />
      <p v-else class="text-center" dir="ltr">Welcome {{ data?.name }}!</p>
      <PButton class="my-4" @click="logout">Logout</PButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PLoading } from '@pey/core';

definePageMeta({
  middleware: ['auth'],
});

const { t } = useI18n();

const logout = useLogout();

const { data, pending } = useGetProfile();
</script>
