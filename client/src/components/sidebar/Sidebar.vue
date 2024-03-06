<template>
  <nav
    class="flex h-full w-60 flex-col overflow-hidden bg-white px-2 py-4 shadow-lg"
  >
    <div class="pb-4 pt-2">
      <PText as="p" class="text-center" weight="bold" variant="h4">
        {{ t('common.appName') }}
      </PText>
    </div>

    <hr class="border-gray-10" />

    <PScrollbar class="-mx-2 grow px-2 py-4">
      <!-- // TODO: create a sidebar nav item component -->
      <NuxtLink v-slot="{ isActive }" class="group" to="/notes">
        <div
          class="flex items-center gap-3 rounded p-2"
          :class="{
            'bg-primary-10': isActive,
            'group-focus:bg-gray-00 hover:bg-gray-00': !isActive,
          }"
        >
          <PText variant="subtitle">📝</PText>
          <PText
            :class="{ 'text-gray-100': isActive, 'text-gray-80': !isActive }"
            :weight="isActive ? 'medium' : 'regular'"
            variant="caption1"
          >
            {{ t('sidebar.notes') }}
          </PText>
        </div>
      </NuxtLink>
    </PScrollbar>

    <hr class="mb-2 border-gray-10" />

    <NuxtLink v-slot="{ isActive }" class="group" to="/profile">
      <div
        class="flex items-center gap-2 overflow-hidden rounded p-2"
        :class="{
          'bg-primary-10': isActive,
          'group-focus:bg-gray-00 hover:bg-gray-00': !isActive,
        }"
      >
        <div
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary-20"
        >
          <PeyUserIcon class="text-primary" :size="20" />
        </div>

        <PLoading v-if="pending" class="text-primary" />
        <PText
          v-else
          :class="{ 'text-gray-100': isActive, 'text-gray-80': !isActive }"
          :weight="isActive ? 'bold' : 'medium'"
          variant="caption1"
        >
          {{ data?.name }}
        </PText>
      </div>
    </NuxtLink>

    <button
      class="flex items-center gap-3 rounded px-4 py-2 hover:bg-gray-00 focus:bg-gray-00"
      type="button"
      @click="logout"
    >
      <PeyLogoutIcon class="text-primary" />
      <PText variant="caption1">
        {{ t('sidebar.logout') }}
      </PText>
    </button>
  </nav>
</template>

<script lang="ts" setup>
import { PLoading, PScrollbar, PText } from '@pey/core';
import { PeyLogoutIcon, PeyUserIcon } from '@pey/icons';

const { t } = useI18n();
const logout = useLogout();
const { data, pending } = useGetProfile();
</script>
