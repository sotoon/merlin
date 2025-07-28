<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <i class="i-mdi-clipboard-text text-h1 text-primary" />

        <PHeading level="h1" responsive>
          {{ t('common.templates') }}
        </PHeading>
      </div>
      <NuxtLink :to="{ name: 'template-create' }">
        <PIconButton class="shrink-0" :icon="PeyPlusIcon" tabindex="-1" />
      </NuxtLink>
    </div>

    <div v-if="isPending" class="flex items-center justify-center py-8">
      <PLoading class="text-primary" :size="20" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('note.getTemplatesError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NoteList v-else-if="notes?.length" :notes="notes" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noTemplates') }}
    </PText>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PLoading, PText } from '@pey/core';
import { PeyPlusIcon, PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'templates' });

const { t } = useI18n();
useHead({ title: t('common.templates') });
const {
  data: notes,
  isPending,
  error,
  refetch,
} = useGetNotes({
  type: NOTE_TYPE.template,
});
</script>
