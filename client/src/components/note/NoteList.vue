<template>
  <ul class="grid grid-cols-1 gap-2 py-4 lg:grid-cols-2 lg:gap-3">
    <li v-for="note in notes" :key="note.uuid">
      <NuxtLink
        :to="
          note.type === 'Template'
            ? {
                name: 'template',
                params: {
                  id: note.uuid,
                },
              }
            : {
                name: 'note',
                params: {
                  type: NOTE_TYPE_ROUTE_PARAM[note.type],
                  id: note.uuid,
                },
              }
        "
      >
        <NoteCard
          :note="note"
          :display-writer="isMessages"
          :display-type="isMessages"
        />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{
  notes: Note[];
  isMessages?: boolean;
}>();
</script>
