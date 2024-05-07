<template>
  <PListbox
    v-model="model"
    hide-details
    :label
    :loading="pending"
    :multiple
    searchable
  >
    <PListboxOption
      v-for="user in users"
      :key="user.uuid"
      :label="`${user.name} (${user.email})`"
      :value="user.email"
    />
  </PListbox>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';

defineProps<{ label?: string; multiple?: boolean }>();
const model = defineModel<string[] | null>();

const { data: users, pending } = useGetUsers();
</script>
