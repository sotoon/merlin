<script lang="ts" setup>
const props = defineProps<{
  profile: Schema<'Profile'>;
}>();

const { t } = useI18n();
useHead({ title: () => props.profile.name || '' });
</script>

<template>
  <div>
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
