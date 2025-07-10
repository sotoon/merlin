<template>
  <div>
    <PListbox
      v-model="model"
      hide-details
      :label
      :loading="pending"
      :multiple
      searchable
    >
      <PListboxOption
        v-for="user in filteredUsers"
        :key="user.uuid"
        :label="user.name || user.email"
        :value="user.email"
      />
    </PListbox>

    <div class="mt-3 flex flex-wrap gap-3">
      <PChip
        v-for="userEmail in model"
        :key="userEmail"
        :label="getUserLabel(userEmail)"
        removable
        size="small"
        @remove="handleRemove(userEmail)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PChip, PListbox, PListboxOption } from '@pey/core';

defineOptions({ inheritAttrs: false });
defineProps<{ label?: string; multiple?: boolean }>();
const model = defineModel<string[] | null>();

const { data: users, pending } = useGetUsers();
const { data: profile } = useGetProfile();

const filteredUsers = computed(() => {
  if (!users.value) return [];

  if (profile.value) {
    return users.value.filter((user) => user.email !== profile.value?.email);
  }

  return users.value;
});

const getUserLabel = (userEmail: string) =>
  users.value?.find((user) => user.email === userEmail)?.name || userEmail;

const handleRemove = (userEmail: string) => {
  model.value = model.value?.filter((email) => email !== userEmail) ?? [];
};
</script>
