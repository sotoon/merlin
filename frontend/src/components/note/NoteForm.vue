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
      <label class="mb-2 flex items-center gap-2 text-md font-bold">
        {{ t('common.content') }}
        <PTooltip>
          <PeyInfoIcon class="h-5 w-5 text-gray-50" />
          <template #content>
            <div class="max-w-sm">
              می‌تونید از قالب‌های پیش‌ساخته استفاده کنید. برای تعریف قالب‌های
              دلخواه خودتون، به بخش میز کار در منوی کناری مراجعه کنید.
            </div>
          </template>
        </PTooltip>
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
          @update:model-value="handleChange"
        />
      </VeeField>
    </div>

    <div>
      <VeeField v-slot="{ componentField }" name="mentioned_users">
        <label class="mb-2 flex items-center gap-2 text-md font-bold">
          {{ t('note.mentionedUsers') }}
          <PTooltip>
            <PeyInfoIcon class="h-5 w-5 text-gray-50" />
            <template #content>
              <div class="max-w-sm">
                با منشن کردن دیگر کاربرها، می‌تونید دسترسی مشاهده‌ی متن‌تون رو
                به اون‌ها بدید. افراد منشن‌ شده می‌تونن برای شما نظر ثبت کنن.
                اما قادر به مشاهده‌ی نظرات دیگران نیستن.
              </div>
            </template>
          </PTooltip>
        </label>
        <UserSelect v-bind="componentField" multiple />
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
        <label class="mb-2 flex items-center gap-2 text-md font-bold">
          {{ t('note.relatedNotes') }}
          <PTooltip>
            <PeyInfoIcon class="h-5 w-5 text-gray-50" />
            <template #content>
              <div class="max-w-sm">
                این جا می‌تونید یادداشت‌های دیگری از هر نوع که به این یادداشت‌
                شما ارتباط دارن اضافه کنید. این کار منجر به دسترسی‌پذیری بهتر
                اون یادداشت‌ها برای تمام افرادی که دسترسی دیدن این مستند رو دارن
                می‌شه.
                <br />
                دقت کنید که دسترسی‌ها به یادداشت‌های لینک‌شده به طور خودکار
                <b>اعطا نمی‌شه</b> و برای این که افرادی که زیر این متن شما منشن
                شدن بتونن متون لینک‌شده‌ی شما رو مشاهده کنن، باید زیر اون‌ها هم
                منشن شده‌باشن.
              </div>
            </template>
          </PTooltip>
        </label>
        <PListbox
          v-bind="componentField"
          hide-details
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
  PTooltip,
} from '@pey/core';
import { PeyInfoIcon } from '@pey/icons';
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
const route = useRoute();
const { data: profile } = useGetProfile();
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
    linked_notes: props.note?.linked_notes?.map((note) => note.uuid) || [],
    proposal_type:
      props.note?.proposal_type ||
      (route.query.proposal_type as ProposalType) ||
      undefined,
  },
});
const { data: notes, isPending: isNotesLoading } = useGetNotes();

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
    ?.filter((note) => {
      if (note.type === NOTE_TYPE.template) return false;
      if (note.uuid === props.note?.uuid) return false;
      if (
        note.type === NOTE_TYPE.feedback &&
        (note.feedback_request_uuid_of_feedback ||
          note.owner === profile.value?.email)
      ) {
        return false;
      }
      return true;
    })
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
