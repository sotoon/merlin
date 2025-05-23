<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

defineProps<{ user: User }>();

const { t } = useI18n();
const route = useRoute();

const {
  data: oneOnOne,
  pending,
  error,
  refresh,
} = useGetOneOnOne({
  userId: String(route.params.userId),
  oneOnOneId: String(route.params.id),
});
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-2 py-8 sm:px-4 lg:px-8 lg:pt-10">
    <PLoading v-if="pending" class="mx-auto text-primary" :size="20" />

    <div v-else-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{
          error.statusCode === 404
            ? t('note.oneOnOneNotFound')
            : t('note.getOneOnOneError')
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

    <NuxtPage v-else-if="oneOnOne" :one-on-one="oneOnOne" :user="user" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noteNotFound') }}
    </PText>
  </PBox>
</template>
