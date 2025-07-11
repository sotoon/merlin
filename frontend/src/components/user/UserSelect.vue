<template>
  <div>
    <PListbox
      v-model="model"
      hide-details
      :label
      :loading="pending"
      :multiple
      :required
      searchable
    >
      <PListboxOption
        v-for="user in filteredUsers"
        :key="user.uuid"
        :label="user.name || user.email"
        :value="user[valueKey]"
      />
    </PListbox>

    <div class="mt-3 flex flex-wrap gap-3">
      <PChip
        v-for="itemValue in model"
        :key="itemValue"
        :label="getUserLabel(itemValue)"
        removable
        size="small"
        @remove="handleRemove(itemValue)"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PChip, PListbox, PListboxOption } from '@pey/core';

defineOptions({ inheritAttrs: false });
const props = withDefaults(
  defineProps<{
    label?: string;
    multiple?: boolean;
    required?: boolean;
    valueKey?: 'email' | 'uuid';
  }>(),
  {
    valueKey: 'email',
  },
);
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

const getUserLabel = (value: string) =>
  users.value?.find((user) => user[props.valueKey] === value)?.name || value;

const handleRemove = (value: string) => {
  model.value = model.value?.filter((item) => item !== value) ?? [];
};
</script>
