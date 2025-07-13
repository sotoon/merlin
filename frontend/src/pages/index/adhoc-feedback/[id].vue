<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';
import { useQueryClient } from '@tanstack/vue-query';

const { t } = useI18n();
const route = useRoute();
const queryClient = useQueryClient();

const {
  data: entry,
  isPending,
  error,
  refetch,
} = useGetAdhocFeedbackEntry(String(route.params.id));

watch(
  () => entry.value?.note,
  (newVal) => {
    if (newVal && !newVal.read_status) {
      const { execute } = useUpdateNoteReadStatus({ id: newVal.uuid });
      execute(true);
      queryClient.invalidateQueries({ queryKey: ['adhoc-feedback-entries'] });
    }
  },
  { once: true },
);

const errorCode = computed(() => (error.value as any)?.response?.status);
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <PLoading v-if="isPending" class="mx-auto text-primary" :size="20" />

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{
          errorCode === 404
            ? t('adhocFeedback.adhocFeedbackNotFound')
            : t('note.getAdhocFeedbackError')
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

    <NuxtPage v-else-if="entry" :entry="entry" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noteNotFound') }}
    </PText>
  </PBox>
</template>
