<template>
  <div>
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

      <VeeField
        v-slot="{ value, handleChange }"
        name="content"
        rules="required"
      >
        <Editor :model-value="value" @update:model-value="handleChange" />
      </VeeField>

      <div v-if="noteType !== NOTE_TYPE.personal">
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

      <div class="flex flex-wrap gap-4">
        <VeeField v-slot="{ componentField }" name="date">
          <PDatePickerInput
            v-bind="componentField"
            :label="
              noteType === NOTE_TYPE.meeting
                ? t('note.meetingDate')
                : t('common.date')
            "
            type="jalali"
          />
        </VeeField>

        <div class="flex flex-wrap gap-2">
          <div class="w-24">
            <VeeField v-slot="{ componentField }" name="year">
              <PListbox
                v-bind="componentField"
                hide-details
                :label="t('note.year')"
              >
                <PListboxOption
                  v-for="year in YEARS"
                  :key="year"
                  :label="year.toLocaleString('fa-IR', { useGrouping: false })"
                  :value="year"
                />
              </PListbox>
            </VeeField>
          </div>

          <div class="w-24">
            <VeeField v-slot="{ componentField }" name="period">
              <PListbox
                v-bind="componentField"
                hide-details
                :label="t('note.period')"
              >
                <PListboxOption
                  v-for="(period, index) in EVALUATION_PERIODS"
                  :key="index"
                  :label="period"
                  :value="index"
                />
              </PListbox>
            </VeeField>
          </div>
        </div>
      </div>

      <div>
        <VeeField v-slot="{ componentField }" name="linked_notes">
          <PListbox
            v-bind="componentField"
            hide-details
            :label="t('note.relatedNotes')"
            :loading="isNotesLoading"
            multiple
            searchable
          >
            <PListboxOption
              v-for="noteItem in noteOptions"
              :key="noteItem.uuid"
              :label="noteItem.title"
              :value="noteItem.uuid"
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
import {
  PButton,
  PDatePickerInput,
  PInput,
  PListbox,
  PListboxOption,
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

const YEARS = [1402, 1403, 1404, 1405, 1406];

const props = defineProps<{
  note?: Note;
  noteType?: NoteType;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: NoteFormValues, ctx: SubmissionContext<NoteFormValues>];
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
    date: props.note?.date ? new Date(props.note.date) : undefined,
    year: props.note?.year || YEARS[1],
    period: props.note?.period || 0,
    linked_notes: props.note?.linked_notes || [],
  },
});
useUnsavedChangesGuard({ disabled: () => !meta.value.dirty });
const { data: users, pending: isUsersLoading } = useGetUsers();
const { data: notes, pending: isNotesLoading } = useGetNotes();

const noteOptions = computed(() =>
  notes.value
    ?.filter(
      (note) =>
        note.type !== NOTE_TYPE.template && note.uuid !== props.note?.uuid,
    )
    .sort(
      (a, b) =>
        new Date(b.date_updated).getTime() - new Date(a.date_updated).getTime(),
    ),
);

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

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});
</script>
