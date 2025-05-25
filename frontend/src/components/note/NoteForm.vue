<template>
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

    <div class="space-y-4 py-2">
      <label id="content-label">
        <PText class="block cursor-default" variant="caption1" weight="bold">
          {{ t('common.content') }}
        </PText>
      </label>

      <NoteTemplateSelect
        :should-confirm="Boolean(formValues.content)"
        @select="handleTemplateSelect"
      />

      <VeeField
        v-slot="{ value, handleChange }"
        name="content"
        rules="required"
      >
        <Editor
          :model-value="value"
          :placeholder="t('note.writeNoteContent')"
          aria-labelledby="content-label"
          @update:model-value="handleChange"
        />
      </VeeField>
    </div>

    <div>
      <VeeField v-slot="{ componentField }" name="mentioned_users">
        <UserSelect
          v-bind="componentField"
          :label="t('note.mentionedUsers')"
          multiple
        />
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
</template>

<script lang="ts" setup>
import {
  PButton,
  PDatePickerInput,
  PInput,
  PListbox,
  PListboxOption,
  PText,
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
  setValues,
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
const { data: notes, pending: isNotesLoading } = useGetNotes();

const isEditing = computed(() => Boolean(props.note));

useUnsavedChangesGuard({
  disabled: () => !isEditing.value || !meta.value.dirty,
});
useStoreDraft({
  disabled: isEditing,
  storageKey: () => `note:draft:${props.noteType}`,
  values: computed(() => ({
    title: formValues.title,
    content: formValues.content,
  })),
  setValues: (values) =>
    setValues({
      ...formValues,
      title: values.title,
      content: values.content,
    }),
});

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
