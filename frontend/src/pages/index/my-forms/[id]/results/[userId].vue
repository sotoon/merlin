<template>
  <FormPreview :form="form" :user-id="Number(route.params.userId)" />
</template>

<script lang="ts" setup>
definePageMeta({ name: 'my-form' });
defineProps<{ form: FormDetails }>();

const route = useRoute();
</script>
