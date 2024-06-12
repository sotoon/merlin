<template>
  <ul class="grid grid-cols-1 gap-2 py-4 lg:gap-3">
    <li v-for="feedback in feedbacks" :key="feedback.uuid">
      <NoteFeedbackForm
        :note="note"
        :feedback="feedback"
        :visible="showFormId === feedback.uuid"
        @update:visible="showFormId = null"
      />

      <NoteFeedbackCard
        v-if="showFormId !== feedback.uuid"
        :note="note"
        :feedback="feedback"
        @edit="showFormId = feedback.uuid"
      />
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{ note: Note; feedbacks: NoteFeedback[] }>();

const showFormId = ref<string | null>(null);
</script>
