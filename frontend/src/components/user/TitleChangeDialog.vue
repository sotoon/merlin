<template>
  <PDialog
    :model-value="open"
    :title="t('common.changeJobTitle')"
    size="medium"
    @update:model-value="handleClose"
  >
    <form class="space-y-4" @submit="onSubmit">
      <VeeField
        v-slot="{ componentField }"
        :label="t('common.newJobTitle')"
        name="new_title"
        rules="required"
      >
        <PInput
          v-bind="componentField"
          hide-details
          :label="t('common.newJobTitle')"
          :placeholder="t('common.newJobTitle')"
          required
        />
      </VeeField>

      <VeeField v-slot="{ value, handleChange }" name="reason">
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-70">
            {{ t('common.reasonForChange') }}
          </label>
          <textarea
            :value="value"
            rows="3"
            class="w-full rounded-md border border-gray-30 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-primary"
            :placeholder="t('common.reasonForChange')"
            @input="handleChange"
          />
        </div>
      </VeeField>

      <VeeField
        v-slot="{ componentField }"
        :label="t('common.effectiveDate')"
        name="effective_date"
        rules="required"
      >
        <PDatePickerInput
          v-bind="componentField"
          hide-details
          :label="t('common.effectiveDate')"
          required
          type="jalali"
        />
      </VeeField>

      <div v-if="error" class="text-sm text-danger">
        {{ error }}
      </div>

      <div class="flex justify-end gap-2 pt-4">
        <PButton
          type="button"
          color="gray"
          :disabled="isPending || !meta.valid || !meta.dirty"
          @click="handleClose"
        >
          {{ t('common.cancel') }}
        </PButton>
        <PButton
          type="submit"
          :loading="isPending"
          :disabled="isPending || !meta.valid || !meta.dirty"
        >
          {{ t('common.save') }}
        </PButton>
      </div>
    </form>
  </PDialog>
</template>

<script lang="ts" setup>
import { PButton, PDialog, PInput, PDatePickerInput } from '@pey/core';
import { useCreateTitleChange } from '~/composables/users/useCreateTitleChange';

const props = defineProps<{
  open: boolean;
  userUuid: string;
  currentTitle: string;
}>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'success'): void;
}>();

const { t } = useI18n();
const { mutate, isPending, error } = useCreateTitleChange();

const { meta, handleSubmit, setValues, resetForm } = useForm<
  Schema<'TitleChangeRequest'>
>({
  initialValues: {
    user: 0,
    old_title: props.currentTitle || 'هیچ',
    new_title: '',
    reason: '',
    effective_date: new Date() as unknown as string,
  },
});

const { data: userData } = useGetUser(props.userUuid);
watch(userData, (newUserData) => {
  if (newUserData) {
    setValues({ user: newUserData.id });
  }
});

function handleClose(newValue: boolean) {
  if (!newValue) {
    emit('close');
    resetForm();
  }
}

const onSubmit = handleSubmit((values) => {
  if (!values.new_title.trim()) {
    return;
  }

  const effectiveDateString = values.effective_date
    ? new Date(values.effective_date).toISOString().split('T')[0]
    : new Date().toISOString().split('T')[0];

  mutate(
    {
      user: values.user,
      old_title: values.old_title,
      new_title: values.new_title,
      reason: values.reason,
      effective_date: effectiveDateString,
    },
    {
      onSuccess: () => {
        emit('success');
        emit('close');
        resetForm();
      },
    },
  );
});

watch(
  () => props.currentTitle,
  (newTitle) => {
    setValues({ old_title: newTitle });
  },
);

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      setValues({
        old_title: props.currentTitle,
        new_title: '',
        reason: '',
        effective_date: new Date() as unknown as string,
      });
    }
  },
);
</script>
