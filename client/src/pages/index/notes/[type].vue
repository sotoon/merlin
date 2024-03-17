<template>
  <div>{{ type }}</div>
</template>

<script lang="ts" setup>
const {
  params: { type },
} = useRoute();
</script>
