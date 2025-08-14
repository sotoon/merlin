<template>
  <div class="flex flex-wrap items-center gap-2">
    <PText class="text-gray-50" variant="caption2">
      {{ t('common.team') }}:
    </PText>

    <div class="w-40">
      <PListbox v-model="selectedTeam" hide-details size="small">
        <PListboxOption :label="t('common.allTeams')" :value="''" />
        <PListboxOption
          v-for="team in teamsList"
          :key="team.id"
          :label="team.name"
          :value="team.name"
        />
      </PListbox>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PListbox, PListboxOption, PText } from '@pey/core';
import { useRouteQuery } from '@vueuse/router';

const { t } = useI18n();
const selectedTeam = useRouteQuery('team', '');

const { data: teams } = useGetTeams();

const teamsList = computed(() => {
  if (!teams.value) return [];
  return teams.value.map((team) => ({
    id: team.id,
    name: team.name,
  }));
});

watch(selectedTeam, (newValue) => {
  const query = { ...useRoute().query };
  if (newValue) {
    query.team = newValue;
  } else {
    delete query.team;
  }
  useRouter().replace({ query });
});
</script>
