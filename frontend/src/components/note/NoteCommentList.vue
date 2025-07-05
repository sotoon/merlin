<template>
  <ul class="grid grid-cols-1 gap-2 py-4 lg:gap-3">
    <li v-for="comment in comments" :key="comment.uuid">
      <PCard header-variant="primary" :title="comment.owner_name">
        <article>
          <EditorContent :content="comment.content" />
        </article>

        <template #toolbar>
          <PIconButton
            v-if="comment.owner === profile?.email"
            :icon="PeyEditIcon"
            variant="ghost"
            @click="
              navigateTo({
                name: 'note-comment',
                query: { owner: comment.owner },
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

defineProps<{ comments: Schema<'Comment'>[] }>();

const { data: profile } = useGetProfile();
</script>
