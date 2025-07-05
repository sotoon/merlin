<script lang="ts" setup>
definePageMeta({ name: 'one-on-one-userId' });

defineProps<{ user: User }>();
</script>

<template>
  <NoteOneOnOneList :user-id="user.uuid" :username="user.name" />
</template>
