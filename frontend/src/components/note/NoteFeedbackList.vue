<template>
  <ul class="grid grid-cols-1 gap-2 py-4 lg:gap-3">
    <li v-for="feedback in feedbacks" :key="feedback.uuid">
      <PCard header-variant="primary" :title="feedback.owner_name">
        <article>
          <EditorContent :content="feedback.content" />
        </article>

        <template #toolbar>
          <PIconButton
            v-if="feedback.owner === profile?.email"
            :icon="PeyEditIcon"
            variant="ghost"
            @click="
              navigateTo({
                name: 'note-feedback',
                query: { owner: feedback.owner },
              })
            "
          />
        </template>
      </PCard>
    </li>
  </ul>
</template>

<script lang="ts" setup>
import { PCard, PIconButton } from '@pey/core';
import { PeyEditIcon } from '@pey/icons';

defineProps<{ feedbacks: NoteFeedback[] }>();

const { data: profile } = useGetProfile();
</script>
