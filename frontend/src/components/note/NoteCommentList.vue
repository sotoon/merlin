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
                name: getCommentRoute(),
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

const props = defineProps<{
  comments: Schema<'Comment'>[];
  type?: 'adhoc' | 'one-on-one';
}>();

const { data: profile } = useGetProfile();

function getCommentRoute() {
  if (props.type === 'adhoc') {
    return 'adhoc-comment';
  } else if (props.type === 'one-on-one') {
    return 'one-on-one-comment';
  }
  return 'note-comment';
}
</script>
