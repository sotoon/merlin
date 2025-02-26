<template>
  <div class="px-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <i
          class="i-mdi-form mb-3 me-4 inline-block align-middle text-h1 text-primary"
        />

        <PText responsive variant="title" weight="bold">
          {{ form.name }}
        </PText>
      </div>

      <PChip v-if="form.is_filled" color="success" :label="t('form.filled')" />
    </div>

    <div class="mt-4">
      <PText
        v-if="results?.assigned_by_name"
        as="p"
        class="text-gray-60"
        variant="caption1"
      >
        {{ t('form.evaluatee') }}: {{ results.assigned_by_name }}
      </PText>
    </div>

    <article class="mt-4 py-4">
      <EditorContent v-if="form.description" :content="form.description" />

      <hr class="my-8 border-gray-10" />

      <PAlert
        v-if="!form.is_expired"
        class="mb-8"
        color="warning"
        :title="t('form.resultsNotAvailable')"
        variant="caution"
      />

      <div
        v-for="(questions, category) in groupedQuestionsByCategory"
        :key="category"
        class="mb-12"
      >
        <div class="flex justify-between gap-2">
          <PText as="h2" variant="subtitle" weight="bold">
            {{ category }}
          </PText>

          <PText
            v-if="results?.categories[category]"
            class="text-gray-60"
            variant="caption1"
          >
            {{ t('form.score') }}:
            <PText class="text-gray-100" variant="body">
              {{ results?.categories[category]?.toLocaleString('fa-IR') }}
            </PText>
          </PText>
        </div>

        <hr class="my-4 border-gray-10" />

        <FormQuestionResult
          v-for="question in questions"
          :key="question.id"
          :question="question"
          :avg="
            results?.questions.find(({ id }) => id === question.id)?.average
          "
        />
      </div>
    </article>
  </div>
</template>

<script lang="ts" setup>
import { PAlert, PChip, PText } from '@pey/core';

const props = defineProps<{ form: FormDetails; userId?: number }>();

const { t } = useI18n();

const { data: allResults } = useGetFormResults(
  {
    formId: props.form.id,
    cycleId: props.form.cycle,
  },
  {
    enabled: props.form.is_expired,
  },
);

const results = computed(
  () =>
    allResults.value?.my_results.find(
      ({ assigned_by }) => assigned_by === props.userId,
    ) ||
    allResults.value?.team_results.find(
      ({ assigned_by }) => assigned_by === props.userId,
    ) ||
    allResults.value?.my_results[0] ||
    allResults.value?.team_results[0],
);

const groupedQuestionsByCategory = computed(() =>
  props.form.questions.reduce(
    (acc, question) => {
      if (!acc[question.category]) {
        acc[question.category] = [];
      }

      acc[question.category].push(question);

      return acc;
    },
    {} as Record<string, Question[]>,
  ),
);
</script>
