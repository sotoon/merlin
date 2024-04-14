<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ note ? t('note.editNote') : t('note.newNote') }}
    </PHeading>

    <NoteTemplateSelect
      :should-confirm="Boolean(formValues.content)"
      @select="handleTemplateSelect"
    />

    <form class="mt-8 space-y-4" @submit="onSubmit">
      <VeeField
        v-slot="{ componentField }"
        :label="t('note.title')"
        name="title"
        rules="required"
      >
        <PInput
          class="grow"
          v-bind="componentField"
          hide-details
          :label="t('note.title')"
          required
        />
      </VeeField>

      <VeeField v-slot="{ componentField }" name="content" rules="required">
        <Editor v-bind="componentField" />
        <!-- <PInput
          v-bind="componentField"
          hide-details
          :rows="8"
          type="textarea"
        /> -->
      </VeeField>

      <div>
        <VeeField v-slot="{ componentField }" name="mentioned_users">
          <PListbox
            v-bind="componentField"
            hide-details
            :label="t('note.mentionedUsers')"
            :loading="isUsersLoading"
            multiple
            searchable
          >
            <PListboxOption
              v-for="user in users"
              :key="user.uuid"
              :label="`${user.name} (${user.email})`"
              :value="user.email"
            />
          </PListbox>
        </VeeField>
      </div>

      <div class="flex flex-wrap items-center justify-end gap-4 pt-8">
        <PButton
          class="shrink-0"
          color="gray"
          type="button"
          variant="light"
          @click="emit('cancel')"
        >
          {{ t('common.cancel') }}
        </PButton>

        <PButton
          class="shrink-0"
          :disabled="!meta.valid || !meta.dirty || isSubmitting"
          :loading="isSubmitting"
          type="submit"
          variant="fill"
        >
          {{ t('common.save') }}
        </PButton>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PInput, PListbox, PListboxOption } from '@pey/core';

const props = defineProps<{
  note?: Note;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteFormValues];
  cancel: [];
}>();

const { t } = useI18n();
const {
  meta,
  values: formValues,
  handleSubmit,
  setFieldValue,
} = useForm<NoteFormValues>({
  initialValues: {
    title: props.note?.title || '',
    content: props.note?.content || '',
    mentioned_users: props.note?.mentioned_users || [],
  },
});
const { data: users, pending: isUsersLoading } = useGetUsers();

const handleTemplateSelect = ({
  action,
  value,
}: {
  action: 'replace' | 'append';
  value: Note | null;
}) => {
  if (action === 'append') {
    setFieldValue(
      'content',
      `${formValues.content}\n\n${value?.content || ''}`,
    );
  } else {
    setFieldValue('content', value?.content || '');
  }
};

const onSubmit = handleSubmit((values) => {
  emit('submit', values);
});
</script>
