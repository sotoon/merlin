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
const { data: currentUser } = useGetProfile();

// Filter out the current user from the list
const filteredUsers = computed(() => {
  if (!users.value || !currentUser.value) return users.value || [];
  return users.value.filter((user) => user.uuid !== currentUser.value?.uuid);
});

const getUserLabel = (userEmail: string) =>
  users.value?.find((user) => user.email === userEmail)?.name || userEmail;

const handleRemove = (userEmail: string) => {
  model.value = model.value?.filter((email) => email !== userEmail) ?? [];
};
</script>
