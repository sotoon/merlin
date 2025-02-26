<template>
  <FormDetail :form="form" />
</template>

<script lang="ts" setup>
definePageMeta({ name: 'form' });
defineProps<{ form: FormDetails }>();
</script>
