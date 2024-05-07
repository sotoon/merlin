<template>
  <ul class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3">
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
                  type: route.params.type || '-',
                  id: note.uuid,
                },
                query: {
                  read:
                    displayReadStatus && !note.read_status ? 'true' : undefined,
                },
              }
        "
      >
        <NoteCard
          :note="note"
          :display-writer="displayWriter"
          :display-type="displayType"
          :display-read-status="displayReadStatus"
        />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{
  notes: Note[];
  displayWriter?: boolean;
  displayType?: boolean;
  displayReadStatus?: boolean;
}>();

const route = useRoute();
</script>
