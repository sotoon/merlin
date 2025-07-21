<script lang="ts" setup>
import { PHeading, PIconButton, PText } from '@pey/core';
import { PeyEditIcon, PeyLogoutIcon, PeyUserIcon } from '@pey/icons';

const props = defineProps<{
  profile: Schema<'Profile'>;
  isCurrentUser?: boolean;
}>();

const { t } = useI18n();
useHead({ title: () => props.profile.name || '' });
const logout = useLogout();
</script>

<template>
  <div>
    <div
      v-if="isCurrentUser"
      class="relative flex justify-between gap-2 border-b border-gray-20 pb-4 sm:items-end"
    >
      <div class="flex flex-col gap-4 overflow-hidden md:flex-row md:items-end">
        <div
          class="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary-20"
        >
          <PeyUserIcon class="text-primary" :size="32" />
        </div>

        <div>
          <PHeading level="h1" responsive>
            {{ profile.name }}
          </PHeading>

          <PText as="p" class="mt-2 text-gray-70" responsive>
            {{ profile.email }}
          </PText>
        </div>
      </div>

      <div class="absolute left-0 flex flex-col items-center gap-3 sm:flex-row">
        <NuxtLink :to="{ name: 'profile-edit' }">
          <PIconButton class="shrink-0" :icon="PeyEditIcon" tabindex="-1" />
        </NuxtLink>

        <PIconButton
          class="shrink-0"
          color="danger"
          :icon="PeyLogoutIcon"
          @click="logout"
        />
      </div>
    </div>

    <div class="p-3">
      <PropertyTable :title="t('profile.organizationInfo')">
        <PropertyTableRow
          :label="t('profile.department')"
          :value="profile.department"
        />

        <PropertyTableRow
          :label="t('profile.chapter')"
          :value="profile.chapter"
        />

        <PropertyTableRow :label="t('profile.team')" :value="profile.team" />

        <PropertyTableRow
          :label="t('profile.leader')"
          :value="profile.leader"
        />

        <PropertyTableRow :label="t('profile.level')" :value="profile.level" />
      </PropertyTable>

      <PropertyTable :title="t('profile.contactInfo')">
        <PropertyTableRow
          :label="t('profile.organizationEmail')"
          :value="profile.email"
        />

        <PropertyTableRow :label="t('profile.gmail')" :value="profile.gmail" />

        <PropertyTableRow :label="t('profile.phone')" :value="profile.phone" />
      </PropertyTable>
    </div>
  </div>
</template>
