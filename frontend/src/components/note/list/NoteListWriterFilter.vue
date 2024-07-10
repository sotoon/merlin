<template>
  <div>
    <PListbox
      :model-value="writerFilter"
      clearable
      hide-details
      :loading="usersPending"
      :placeholder="t('note.writer')"
      size="small"
      @update:model-value="
        (value) => (writerFilter = value === '' ? undefined : value)
      "
    >
      <PListboxOption
        v-for="{ name, email, uuid } in writers"
        :key="uuid"
        :label="name"
        :value="email"
      />
    </PListbox>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const props = defineProps<{ notes: Note[] }>();

const { t } = useI18n();
const writerFilter = useRouteQuery<string>('writer', undefined);
const { data: users, pending: usersPending } = useGetUsers();

const noteOwners = computed(
  () => new Set(props.notes.map((note) => note.owner)),
);
const writers = computed(() =>
  users.value?.filter(({ email }) => noteOwners.value.has(email)),
);
</script>
