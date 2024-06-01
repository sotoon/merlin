<template>
  <PDialog
    v-model="isOpen"
    size="small"
    :title="t('common.performanceManagementGuide')"
  >
    <PText as="p">
      {{ t('guide.notifyMessage') }}
    </PText>

    <template #footer>
      <NuxtLink class="w-full rounded" target="_blank" :to="GUIDE_DRIVE_LINK">
        <PButton
          type="button"
          aria-hidden="true"
          class="w-full"
          :icon-end="PeyOpenInNewIcon"
          size="large"
          variant="fill"
        >
          {{ t('guide.docsFolder') }}
        </PButton>
      </NuxtLink>
    </template>
  </PDialog>
</template>

<script lang="ts" setup>
import { PButton, PDialog, PText } from '@pey/core';
import { PeyOpenInNewIcon } from '@pey/icons';

const GUIDE_NOTIFIED_STORAGE_KEY = 'guide:notified';

const isOpen = ref(false);

const { t } = useI18n();

onMounted(() => {
  if (localStorage.getItem(GUIDE_NOTIFIED_STORAGE_KEY)) {
    return;
  }

  isOpen.value = true;
});

watch(isOpen, () => {
  if (!isOpen.value) {
    localStorage.setItem(GUIDE_NOTIFIED_STORAGE_KEY, 'true');
  }
});
</script>
