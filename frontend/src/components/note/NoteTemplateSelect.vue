<template>
  <div class="max-w-xs">
    <PListbox
      :key="selectionDraft?.uuid"
      clearable
      hide-details
      :loading="isTemplatesLoading || isSharedTemplatesLoading"
      :model-value="selectedValue"
      :placeholder="t('note.selectTemplate')"
      @update:model-value="handleUpdateValue"
    >
      <PListboxOption
        v-for="template in [...(templates || []), ...(sharedTemplates || [])]"
        :key="template.uuid"
        :label="template.title"
        :value="template"
        @click="selectValue(template)"
      />
    </PListbox>
  </div>

  <PDialog
    v-model="showConfirm"
    :title="t('note.useTemplate', { title: selectionDraft?.title })"
    @after-close="dropSelectionDraft"
  >
    <PText>
      {{ t('note.useTemplateConfirmMessage') }}
    </PText>

    <template #footer>
      <div class="flex flex-row-reverse flex-wrap justify-between gap-2">
        <div class="flex flex-row-reverse flex-wrap gap-2">
          <PButton variant="ghost" @click="handleConfirm('replace')">
            {{ t('note.replace') }}
          </PButton>

          <PButton variant="ghost" @click="handleConfirm('append')">
            {{ t('note.append') }}
          </PButton>
        </div>

        <PButton color="gray" variant="ghost" @click="handleConfirmCancel">
          {{ t('common.cancel') }}
        </PButton>
      </div>
    </template>
  </PDialog>
</template>

<script lang="ts" setup>
import { PButton, PDialog, PListbox, PListboxOption, PText } from '@pey/core';

type SelectAction = 'replace' | 'append';

const props = defineProps<{ shouldConfirm?: boolean }>();
const emit = defineEmits<{
  select: [{ action: SelectAction; value: string | null }];
}>();

const selectedValue = ref<Note | null>(null);
const selectionDraft = ref<Note | null>(null);
const showConfirm = ref(false);

const { t } = useI18n();
const { data: templates, pending: isTemplatesLoading } = useGetTemplates();
// TODO: integrate shared templates in the templates api
const { data: sharedTemplates, pending: isSharedTemplatesLoading } =
  useGetNotes({
    type: NOTE_TYPE.template,
    retrieveMentions: true,
  });

const handleUpdateValue = (value: Note | '') => {
  if (!value) {
    selectedValue.value = null;
  }
};

const selectValue = (value: Note) => {
  if (props.shouldConfirm) {
    selectionDraft.value = value;
    showConfirm.value = true;

    return;
  }

  selectedValue.value = value;
  emit('select', { action: 'replace', value: value.uuid });
};

const handleConfirm = (action: SelectAction) => {
  selectedValue.value = selectionDraft.value;
  emit('select', { action, value: selectedValue.value?.uuid || null });
  showConfirm.value = false;
};

const handleConfirmCancel = () => {
  showConfirm.value = false;
};

const dropSelectionDraft = () => {
  selectionDraft.value = null;
};
</script>
