<template>
  <div class="container">
    <p class="text-center text-lg text-primary">
      {{ t('common.appName') }}
    </p>
  </div>
</template>

<script lang="ts" setup>
definePageMeta({
  middleware: ['auth'],
});

const { t } = useI18n();
</script>
