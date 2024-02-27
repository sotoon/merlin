<template>
  <form class="space-y-2" dir="ltr" @submit="onSubmit">
    <VeeField
      v-slot="{ errorMessage, value, handleChange }"
      name="email"
      :label="t('login.email')"
      rules="required|email"
    >
      <PInput
        autofocus
        :error="errorMessage"
        name="email"
        :label="t('login.email')"
        type="email"
        :model-value="value"
        show-error
        @update:model-value="handleChange"
      />
    </VeeField>

    <VeeField
      v-slot="{ errorMessage, value, handleChange }"
      name="password"
      :label="t('login.password')"
      rules="required"
    >
      <PInput
        :error="errorMessage"
        name="password"
        :label="t('login.password')"
        type="password"
        :model-value="value"
        show-error
        @update:model-value="handleChange"
      />
    </VeeField>

    <PButton class="w-full" :icon-start="PeyLockOpenIcon" variant="fill">
      {{ t('login.login') }}
    </PButton>
  </form>
</template>

<script lang="ts" setup>
import { PButton, PInput } from '@pey/core';
import { PeyLockOpenIcon } from '@pey/icons';

interface LoginFormValues {
  email: string;
  password: string;
}

const { t } = useI18n();
const { handleSubmit } = useForm<LoginFormValues>();

const onSubmit = handleSubmit((value) => {
  console.log(value);
});
</script>
