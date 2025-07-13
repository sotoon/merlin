<script lang="ts" setup>
import {
  PButton,
  PListbox,
  PListboxOption,
  PText,
  PAccordionGroup,
  PAccordion,
  PCheckboxGroup,
  PCheckbox,
  PLoading,
} from '@pey/core';
import type { SubmissionContext } from 'vee-validate';
import { ONE_ON_ONE_PLACEHOLDERS } from '~/constants/placeholders';

const props = defineProps<{
  user: User;
  oneOnOne?: Schema<'OneOnOne'>;
  isSubmitting?: boolean;
}>();

const emit = defineEmits<{
  submit: [
    values: Schema<'OneOnOneRequest'>,
    ctx: SubmissionContext<Schema<'OneOnOneRequest'>>,
  ];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit, setValues, values } = useForm<
  Schema<'OneOnOneRequest'>
>({
  initialValues: {
    tags: props.oneOnOne?.tags || [],
    personal_summary: props.oneOnOne?.personal_summary || '',
    career_summary: props.oneOnOne?.career_summary || '',
    communication_summary: props.oneOnOne?.communication_summary || '',
    performance_summary: props.oneOnOne?.performance_summary || '',
    actions: props.oneOnOne?.actions || '',
    leader_vibe: props.oneOnOne?.leader_vibe,
    extra_notes: props.oneOnOne?.extra_notes || '',
    linked_notes: props.oneOnOne?.note?.linked_notes || [],
  },
  validationSchema: {
    personal_summary: '',
    career_summary: '',
    communication_summary: '',
    performance_summary: 'required|max:800',
    actions: '',
    extra_notes: '',
    leader_vibe: 'required',
  },
});

const selectedTags = ref<number[]>([]);

const VIBES = [':)', ':|', ':('] as Schema<'LeaderVibeEnum'>[];
const EXCLUDES_TOOLBARS = ['table'];

watch(selectedTags, (newValue) => {
  setValues({ tags: newValue });
});

watch(
  () => props.oneOnOne,
  (newValue) => {
    if (!newValue) return;
    selectedTags.value = newValue.tags;
  },
  { immediate: true },
);

const { data: tags, isPending: isTagsLoading } = useGetOneOnOneTags();
const personalTags = computed(() =>
  (tags.value || []).filter((tag) => tag.section === 'personal'),
);
const careerTags = computed(() =>
  (tags.value || []).filter((tag) => tag.section === 'career'),
);
const communicationTags = computed(() =>
  (tags.value || []).filter((tag) => tag.section === 'communication'),
);
const performanceTags = computed(() =>
  (tags.value || []).filter((tag) => tag.section === 'performance'),
);

const { data: notes, pending: isNotesLoading } = useGetNotes();
const noteOptions = computed(() =>
  notes.value
    ?.filter(
      (note) =>
        note.type !== NOTE_TYPE.template &&
        !(
          note.type === NOTE_TYPE.feedback &&
          note.feedback_request_uuid_of_feedback
        ),
    )
    .sort(
      (a, b) =>
        new Date(b.date_updated).getTime() - new Date(a.date_updated).getTime(),
    ),
);

const onSubmit = handleSubmit((values, ctx) => {
  emit('submit', values, ctx);
});

const isEditing = computed(() => Boolean(props.oneOnOne));

useUnsavedChangesGuard({
  disabled: () => !isEditing.value || !meta.value.dirty,
});
useStoreDraft({
  disabled: isEditing,
  storageKey: () => 'note:draft:oneOnOne',
  values: computed(() => ({
    personal_summary: values.personal_summary,
    career_summary: values.career_summary,
    communication_summary: values.communication_summary,
    performance_summary: values.performance_summary,
    actions: values.actions,
    extra_notes: values.extra_notes,
    tags: values.tags,
    leader_vibe: values.leader_vibe,
    linked_notes: values.linked_notes,
  })),
  setValues: (values) => {
    setValues({
      ...values,
    });
    selectedTags.value = values.tags;
  },
});
</script>

<template>
  <form class="mt-8 space-y-4" @submit="onSubmit">
    <PLoading v-if="isTagsLoading" class="mx-auto text-primary" />
    <template v-else>
      <PAccordionGroup icon-end multiple active-variant="primary">
        <PAccordion :title="t('oneOnOne.individualDimension')">
          <div class="space-y-4">
            <label id="content-label">
              <PText
                class="block cursor-default"
                variant="caption1"
                weight="bold"
              >
                {{ t('oneOnOne.whatWeTalkedAbout') }}
              </PText>
            </label>

            <VeeField
              v-slot="{ value, handleChange, errorMessage }"
              name="personal_summary"
            >
              <Editor
                :model-value="value"
                :extends-toolbars="EXCLUDES_TOOLBARS"
                :placeholder="ONE_ON_ONE_PLACEHOLDERS.personal_summary"
                aria-labelledby="content-label"
                @update:model-value="handleChange"
              />
              <div v-if="errorMessage" class="mt-1 text-sm text-danger">
                {{ t('messages.max', { length: 700 }) }}
              </div>
            </VeeField>

            <div class="space-y-4">
              <label id="tags-label">
                <PText
                  class="block cursor-default"
                  variant="caption1"
                  weight="bold"
                >
                  {{ t('oneOnOne.whatWeTalkedAboutOptions') }}
                </PText>
              </label>

              <PCheckboxGroup
                v-model="selectedTags"
                flow="vertical"
                aria-labelledby="tags-label"
              >
                <PCheckbox
                  v-for="tag in personalTags"
                  :key="tag.id"
                  :value="tag.id"
                >
                  {{ tag.name_fa }}
                </PCheckbox>
              </PCheckboxGroup>
            </div>
          </div>
        </PAccordion>
        <PAccordion :title="t('oneOnOne.growthPath')">
          <div class="space-y-4">
            <label id="content-label">
              <PText
                class="block cursor-default"
                variant="caption1"
                weight="bold"
              >
                {{ t('oneOnOne.whatWeTalkedAbout') }}
              </PText>
            </label>

            <VeeField
              v-slot="{ value, handleChange, errorMessage }"
              name="career_summary"
            >
              <Editor
                :model-value="value"
                :extends-toolbars="EXCLUDES_TOOLBARS"
                :placeholder="ONE_ON_ONE_PLACEHOLDERS.career_summary"
                aria-labelledby="content-label"
                @update:model-value="handleChange"
              />
              <div v-if="errorMessage" class="mt-1 text-sm text-danger">
                {{ t('messages.max', { length: 700 }) }}
              </div>
            </VeeField>

            <div class="space-y-4">
              <label id="tags-label">
                <PText
                  class="block cursor-default"
                  variant="caption1"
                  weight="bold"
                >
                  {{ t('oneOnOne.whatWeTalkedAboutOptions') }}
                </PText>
              </label>

              <PCheckboxGroup
                v-model="selectedTags"
                flow="vertical"
                aria-labelledby="tags-label"
              >
                <PCheckbox
                  v-for="tag in careerTags"
                  :key="tag.id"
                  :value="tag.id"
                >
                  {{ tag.name_fa }}
                </PCheckbox>
              </PCheckboxGroup>
            </div>
          </div>
        </PAccordion>
        <PAccordion :title="t('oneOnOne.interactionAndCustomerOrientation')">
          <div class="space-y-4">
            <label id="content-label">
              <PText
                class="block cursor-default"
                variant="caption1"
                weight="bold"
              >
                {{ t('oneOnOne.whatWeTalkedAbout') }}
              </PText>
            </label>

            <VeeField
              v-slot="{ value, handleChange, errorMessage }"
              name="communication_summary"
            >
              <Editor
                :model-value="value"
                :extends-toolbars="EXCLUDES_TOOLBARS"
                :placeholder="ONE_ON_ONE_PLACEHOLDERS.communication_summary"
                aria-labelledby="content-label"
                @update:model-value="handleChange"
              />
              <div v-if="errorMessage" class="mt-1 text-sm text-danger">
                {{ t('messages.max', { length: 700 }) }}
              </div>
            </VeeField>

            <div class="space-y-4">
              <label id="tags-label">
                <PText
                  class="block cursor-default"
                  variant="caption1"
                  weight="bold"
                >
                  {{ t('oneOnOne.whatWeTalkedAboutOptions') }}
                </PText>
              </label>

              <PCheckboxGroup
                v-model="selectedTags"
                flow="vertical"
                aria-labelledby="tags-label"
              >
                <PCheckbox
                  v-for="tag in communicationTags"
                  :key="tag.id"
                  :value="tag.id"
                >
                  {{ tag.name_fa }}
                </PCheckbox>
              </PCheckboxGroup>
            </div>
          </div>
        </PAccordion>
        <PAccordion :title="`${t('oneOnOne.performanceManagement')} *`">
          <div class="space-y-4">
            <label id="content-label">
              <PText
                class="block cursor-default"
                variant="caption1"
                weight="bold"
              >
                {{ t('oneOnOne.whatWeTalkedAbout') }}
                <span class="text-danger">*</span>
              </PText>
            </label>

            <VeeField
              v-slot="{ value, handleChange, errorMessage }"
              name="performance_summary"
              rules="required"
            >
              <Editor
                :model-value="value"
                :extends-toolbars="EXCLUDES_TOOLBARS"
                :placeholder="ONE_ON_ONE_PLACEHOLDERS.performance_summary"
                aria-labelledby="content-label"
                @update:model-value="handleChange"
              />
              <div v-if="errorMessage" class="mt-1 text-sm text-danger">
                {{ t('messages.max', { length: 700 }) }}
              </div>
            </VeeField>

            <div class="space-y-4">
              <label id="tags-label">
                <PText
                  class="block cursor-default"
                  variant="caption1"
                  weight="bold"
                >
                  {{ t('oneOnOne.whatWeTalkedAboutOptions') }}
                </PText>
              </label>

              <PCheckboxGroup
                v-model="selectedTags"
                flow="vertical"
                aria-labelledby="tags-label"
              >
                <PCheckbox
                  v-for="tag in performanceTags"
                  :key="tag.id"
                  :value="tag.id"
                >
                  {{ tag.name_fa }}
                </PCheckbox>
              </PCheckboxGroup>
            </div>
          </div>
        </PAccordion>
      </PAccordionGroup>

      <div class="my-4 space-y-4">
        <label id="actions">
          <PText class="block cursor-default" variant="caption1" weight="bold">
            {{ t('oneOnOne.whatActionsWeDefined') }}
          </PText>
        </label>

        <VeeField v-slot="{ value, handleChange, errorMessage }" name="actions">
          <Editor
            :model-value="value"
            :extends-toolbars="EXCLUDES_TOOLBARS"
            :placeholder="ONE_ON_ONE_PLACEHOLDERS.actions"
            aria-labelledby="actions"
            @update:model-value="handleChange"
          />
          <div v-if="errorMessage" class="mt-1 text-sm text-danger">
            {{ t('messages.max', { length: 700 }) }}
          </div>
        </VeeField>
      </div>

      <div class="my-4 space-y-4">
        <label id="extra_notes">
          <PText class="block cursor-default" variant="caption1" weight="bold">
            {{ t('oneOnOne.additionalNotes') }}
          </PText>
        </label>

        <VeeField
          v-slot="{ value, handleChange, errorMessage }"
          name="extra_notes"
        >
          <Editor
            :model-value="value"
            :extends-toolbars="EXCLUDES_TOOLBARS"
            :placeholder="ONE_ON_ONE_PLACEHOLDERS.extra_notes"
            aria-labelledby="extra_notes"
            @update:model-value="handleChange"
          />
          <div v-if="errorMessage" class="mt-1 text-sm text-danger">
            {{ t('messages.max', { length: 700 }) }}
          </div>
        </VeeField>
      </div>

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

      <VeeField
        v-slot="{ value, handleChange }"
        name="leader_vibe"
        rules="required"
      >
        <div class="space-y-4">
          <label id="mood-label">
            <PText
              class="text-gray-700 block cursor-default"
              variant="caption1"
              weight="bold"
            >
              {{
                t('oneOnOne.howWasTheMeetingVibeLeader', { name: user.name })
              }}
            </PText>
          </label>

          <div class="flex items-center gap-3" aria-labelledby="mood-label">
            <button
              v-for="vibe in VIBES"
              :key="vibe"
              type="button"
              class="rounded-xl border-2 p-3 py-2 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
              :class="
                value === vibe
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-300 hover:border-gray-400'
              "
              @click="handleChange(vibe)"
            >
              {{ getVibeEmoji(vibe) }}
            </button>
          </div>
        </div>
      </VeeField>

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
    </template>
  </form>
</template>
