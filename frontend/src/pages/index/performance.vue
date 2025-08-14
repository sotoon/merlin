<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import {
  PButton,
  PHeading,
  PTable,
  PTableColumn,
  PPagination,
  PBox,
  PText,
} from '@pey/core';
import { PeyRetryIcon } from '@pey/icons';

definePageMeta({ name: 'performance-list' });

const { t } = useI18n();
const route = useRoute();
const { data: teams } = useGetTeams();

const selectedTeam = computed(() => {
  return teams.value?.find((team) => team.name === route.query.team);
});

const currentPage = ref(1);
const params = computed(() => ({
  page: currentPage.value,
  team: selectedTeam.value?.id as unknown as string,
  ladder: route.query.ladder as string,
  ordering: route.query.ordering as string,
  // q: route.query.q as string,
  as_of: route.query.as_of as string,
}));

watch(
  () => [
    route.query.team,
    route.query.ladder,
    route.query.ordering,
    // route.query.q,
    route.query.as_of,
  ],
  () => {
    currentPage.value = 1;
  },
);

const { data, isPending, error, refetch } = useGetPerformanceList(params);

const totalItems = ref(0);
watch(
  data,
  (newData) => {
    if (newData?.count !== undefined) {
      totalItems.value = newData.count;
    }
  },
  { immediate: true },
);

useHead({
  title: t('common.performanceTable'),
});
</script>

<template>
  <div class="space-y-2 px-4 py-8 lg:px-8 lg:pt-10">
    <div
      class="flex items-center justify-between gap-2 border-b border-gray-20 pb-4"
    >
      <div class="flex items-center gap-4">
        <PHeading level="h1" responsive>
          {{ t('common.performanceTable') }}
        </PHeading>
      </div>

      <PerformanceExportButton />
    </div>

    <PerformanceFilters>
      <!-- <PerformanceSearchFilter /> -->
      <template #sort>
        <PerformanceSortControl />
      </template>
      <template #filter>
        <PerformanceTeamFilter />
        <PerformanceLadderFilter />
        <PerformanceDateFilter />
      </template>
    </PerformanceFilters>

    <div v-if="error" class="flex flex-col items-center gap-4 py-8">
      <PText as="p" class="text-center text-danger" responsive>
        {{ t('user.getUsersError') }}
      </PText>

      <PButton color="gray" :icon-start="PeyRetryIcon" @click="refetch">
        {{ t('common.retry') }}
      </PButton>
    </div>

    <PBox v-else class="bg-white p-4">
      <PTable
        :data="data?.results || []"
        :items-per-page="10"
        :searchable="false"
        :loading="isPending"
        class="border-none !shadow-none"
      >
        <PTableColumn type="index" />
        <PTableColumn label="نام" prop="name" />
        <PTableColumn label="تیم" prop="team" />
        <PTableColumn label="لیدر" prop="leader" />
        <PTableColumn label="لدر" prop="ladder" />
        <PTableColumn label="سطح کلی" prop="overall_level" />
        <PTableColumn label="پله حقوقی" prop="pay_band" />
        <PTableColumn label="تغییر حقوق" prop="salary_change" />
        <PTableColumn
          label="کمیته‌های سال جاری"
          prop="committees_current_year"
        />
        <PTableColumn label="آخرین پاداش" prop="last_bonus_percentage" />
        <PTableColumn label="آخرین تاریخ کمیته">
          <template #default="{ row }: { row: Schema<'UserPerformanceData'> }">
            <PText v-if="row.last_committee_date" variant="caption1">
              {{
                new Date(row.last_committee_date).toLocaleDateString('fa-IR')
              }}
            </PText>
          </template>
        </PTableColumn>
        <PTableColumn label="جزئیات">
          <template #default="{ row }: { row: Schema<'UserPerformanceData'> }">
            <NuxtLink :to="{ name: 'user-detail', params: { id: row.uuid } }">
              <PButton size="small" color="primary">
                {{ t('common.details') }}
              </PButton>
            </NuxtLink>
          </template>
        </PTableColumn>
      </PTable>

      <div class="mt-4 flex w-full items-center justify-end">
        <PPagination
          :total="totalItems"
          :page="currentPage"
          :show-size-picker="false"
          @page-change="({ page }) => (currentPage = page as unknown as number)"
        />
      </div>
    </PBox>
  </div>
</template>
