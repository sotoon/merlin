<script lang="ts" setup>
import { PBox, PButton, PLoading, PText } from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

defineProps<{ user: User }>();

const { t } = useI18n();
const route = useRoute();

const {
  data: oneOnOne,
  isPending,
  error,
  refetch,
} = useGetOneOnOne({
  userId: String(route.params.userId),
  oneOnOneId: String(route.params.id),
});

watch(
  () => oneOnOne.value?.note,
  (newVal) => {
    const isTeamLeader = oneOnOne.value?.leader_vibe;

    if (newVal && !isTeamLeader && !newVal.read_status) {
      const { execute } = useUpdateNoteReadStatus({ id: newVal.uuid });
      execute(true);
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
            ? t('note.oneOnOneNotFound')
            : t('note.getOneOnOneError')
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

    <NuxtPage v-else-if="oneOnOne" :one-on-one="oneOnOne" :user="user" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('note.noteNotFound') }}
    </PText>
  </PBox>
</template>
