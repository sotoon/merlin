<template>
  <NoteDetail :note="note" />
</template>

<script lang="ts" setup>
definePageMeta({ name: 'note' });
defineProps<{ note: Note }>();
</script>
