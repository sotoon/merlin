<script lang="ts" setup>
import { PText, PLoading } from '@pey/core';

const props = defineProps<{ users: User[]; pendingUsers: boolean }>();

const { t } = useI18n();
const route = useRoute();

const { data: profile, isLoading } = useGetProfile();

const user = computed(() => {
  if (route.params.userId === profile.value?.uuid) {
    return profile.value;
  }

  return props.users.find((user) => user.uuid === route.params.userId);
});
</script>

<template>
  <div>
    <div
      v-if="pendingUsers || isLoading"
      class="flex items-center justify-center py-8"
    >
      <PLoading class="text-primary" :size="20" />
    </div>

    <NuxtPage v-else-if="user" :user="user" />

    <PText v-else as="p" class="py-8 text-center text-gray-80" responsive>
      {{ t('oneOnOne.memberNotFound') }}
    </PText>
  </div>
</template>
