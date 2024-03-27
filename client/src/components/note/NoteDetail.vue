<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<!-- eslint-disable vue/no-v-html -->
<template>
  <div>
    <NoteForm
      v-if="isEditMode"
      :note="note"
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />

    <div v-else-if="note">
      <div class="flex items-center justify-between gap-4">
        <PHeading class="px-4" responsive>
          {{ note.title }}
        </PHeading>

        <PIconButton
          class="shrink-0"
          :icon="PeyEditIcon"
          type="button"
          @click="isEditMode = true"
        />
      </div>

      <div class="p-4" v-html="note.content" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PHeading, PIconButton } from '@pey/core';
import { PeyEditIcon } from '@pey/icons';

const props = defineProps<{
  note: Note;
}>();

const isEditMode = ref(!props.note);

const { execute: updateNote, pending } = useUpdateNote({ id: props.note.uuid });

const handleSubmit = (values: NoteFormValues) => {
  updateNote({
    body: values,
    onSuccess: () => {
      isEditMode.value = false;
    },
  });
};

const handleCancel = () => {
  isEditMode.value = false;
};
</script>
