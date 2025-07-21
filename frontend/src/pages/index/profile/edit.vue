<template>
  <div>
    <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
      {{ t('profile.editProfile') }}
    </PHeading>

    <ProfileForm
      :profile="profile"
      :is-submitting="pending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </div>
</template>

<script lang="ts" setup>
import { PHeading } from '@pey/core';

definePageMeta({ name: 'profile-edit' });
defineProps<{ profile: Schema<'Profile'> }>();

const { t } = useI18n();
const { execute: updateProfile, pending } = useUpdateProfile();

const handleSubmit = (values: ProfileFormValues) => {
  updateProfile({
    body: values,
    onSuccess: () => {
      navigateTo({ name: 'profile' });
    },
  });
};

const handleCancel = () => {
  navigateTo({ name: 'profile' });
};
</script>
