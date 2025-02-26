<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <PLoading v-if="pending" class="mx-auto text-primary" :size="20" />

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        <!-- // TODO: change texts -->
        {{
          error.statusCode === 404
            ? t('note.noteNotFound')
            : t('note.getNoteError')
        }}
      </PText>

      <PButton
        v-if="error.statusCode !== 404"
        color="gray"
        :icon-start="PeyRetryIcon"
        @click="refresh"
      >
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NuxtPage v-else-if="form" :form="form" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      <!-- // TODO: change text -->
      {{ t('note.noteNotFound') }}
    </PText>
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const { t } = useI18n();
const route = useRoute();

const formId = computed(() => {
  if (typeof route.params.id === 'string') {
    return route.params.id;
  }

  return '';
});

const { data: form, pending, error, refresh } = useGetForm(formId.value);
</script>
