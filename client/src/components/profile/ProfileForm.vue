<template>
  <form class="space-y-4" @submit="onSubmit">
    <VeeField
      v-slot="{ componentField, errorMessage }"
      name="name"
      rules="required"
    >
      <PInput
        v-bind="componentField"
        dir="auto"
        :error="errorMessage"
        :label="t('profile.name')"
        required
      />
    </VeeField>

    <PInput
      dir="auto"
      hide-details
      :label="t('profile.organizationEmail')"
      :model-value="profile.email"
      disabled
      required
    />

    <VeeField
      v-slot="{ componentField, errorMessage }"
      name="gmail"
      rules="email"
    >
      <PInput
        v-bind="componentField"
        dir="auto"
        :error="errorMessage"
        hide-details
        :label="t('profile.gmail')"
        type="email"
      />
    </VeeField>

    <VeeField
      v-slot="{ componentField, errorMessage }"
      name="phone"
      rules="tel"
    >
      <PInput
        v-bind="componentField"
        :error="errorMessage"
        hide-details
        :label="t('profile.phone')"
        type="tel"
      />
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
  </form>
</template>

<script lang="ts" setup>
import { PButton, PInput } from '@pey/core';

const props = defineProps<{
  profile: User;
  isSubmitting?: boolean;
}>();
const emit = defineEmits<{
  submit: [values: ProfileFormValues];
  cancel: [];
}>();

const { t } = useI18n();
const { meta, handleSubmit } = useForm<ProfileFormValues>({
  initialValues: {
    name: props.profile.name,
    gmail: props.profile.gmail,
    phone: props.profile.phone,
  },
});

const onSubmit = handleSubmit((values) => {
  emit('submit', values);
});
</script>
