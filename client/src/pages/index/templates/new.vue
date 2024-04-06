<template>
  <PBox class="bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('note.newTemplate') }}
    </PHeading>

    <NoteTemplateForm
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>

<script lang="ts" setup>
import { PBox, PHeading } from '@pey/core';

definePageMeta({ name: 'template-create' });

const { t } = useI18n();
const { execute: createNote, pending } = useCreateNote();

const handleSubmit = (values: NoteFormValues) => {
  const date = new Date();
  const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;

  createNote({
    body: { ...values, date: dateString, type: NOTE_TYPE.template },
    onSuccess: () => {
      navigateTo({ name: 'templates' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'templates' });
};
</script>
