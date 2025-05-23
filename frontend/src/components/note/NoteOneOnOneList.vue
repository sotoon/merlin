<script lang="ts" setup>
import { PText } from '@pey/core';

const props = defineProps<{ userId: string; username: string }>();

const { t } = useI18n();

const { data, pending } = useGetOneOnOneList({
  userId: props.userId,
});
</script>

<template>
  <ul
    v-if="data?.length"
    class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3"
  >
    <li v-for="oneOnOne in data" :key="oneOnOne.id">
      <NuxtLink
        :to="{ name: 'one-on-one-id', params: { userId, id: oneOnOne.id } }"
      >
        <NoteOneOnOneCard :one-on-one="oneOnOne" :username="username" />
      </NuxtLink>
    </li>
  </ul>
  <PText
    v-else-if="!pending"
    as="p"
    class="py-8 text-center text-gray-80"
    responsive
  >
    {{ t('oneOnOne.oneOnOneNotFound') }}
  </PText>
</template>
