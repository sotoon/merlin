<template>
  <div>
    <div
      class="flex items-end justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-end gap-4">
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

      <NuxtLink :to="{ name: 'profile-edit' }">
        <PIconButton class="shrink-0" :icon="PeyEditIcon" tabindex="-1" />
      </NuxtLink>
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

<script lang="ts" setup>
import { PHeading, PIconButton, PText } from '@pey/core';
import { PeyEditIcon, PeyUserIcon } from '@pey/icons';

definePageMeta({ name: 'profile' });
const props = defineProps<{ profile: User }>();

const { t } = useI18n();

useHead({ title: () => props.profile.name });
</script>
