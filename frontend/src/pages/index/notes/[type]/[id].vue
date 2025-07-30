<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <PLoading v-if="isPending" class="text-primary" :size="20" />

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{
          errorCode === 404 ? t('note.noteNotFound') : t('note.getNoteError')
        }}
      </PText>

      <PButton
        v-if="errorCode !== 404"
        color="gray"
        :icon-start="PeyRetryIcon"
        @click="refetch"
      >
        {{ t('common.retry') }}
      </PButton>
    </div>

    <NuxtPage v-else-if="note" :note="note" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noteNotFound') }}
    </PText>
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

const { t } = useI18n();
const route = useRoute();

const noteId = computed(() => {
  if (typeof route.params.id === 'string') {
    return route.params.id;
  }

  return '';
});

const { execute: updateNoteReadStatus } = useUpdateNoteReadStatus({
  id: noteId.value,
});
const {
  data: note,
  isPending,
  error,
  refetch,
} = useGetNote(noteId.value, {
  onResponse: route.query.read ? () => updateNoteReadStatus(true) : undefined,
});

const errorCode = computed(() => (error.value as any)?.response?.status);
</script>
