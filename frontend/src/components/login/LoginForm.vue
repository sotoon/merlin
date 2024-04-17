<template>
  <form class="space-y-2" @submit="onSubmit">
    <VeeField
      v-slot="{ errorMessage, value, handleChange }"
      name="email"
      :label="t('login.email')"
      rules="required|email"
    >
      <PInput
        autofocus
        dir="ltr"
        :error="errorMessage"
        name="email"
        :label="t('login.email')"
        type="email"
        :model-value="value"
        required
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
        dir="ltr"
        :error="errorMessage"
        name="password"
        :label="t('login.password')"
        type="password"
        :model-value="value"
        required
        show-error
        @update:model-value="handleChange"
      />
    </VeeField>

    <PButton
      class="w-full"
      :disabled="pending"
      :loading="pending"
      :icon-start="PeyLockOpenIcon"
      variant="fill"
    >
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
const { execute: login, pending } = useLogin();

const onSubmit = handleSubmit((values) => {
  login({ body: values });
});
</script>
