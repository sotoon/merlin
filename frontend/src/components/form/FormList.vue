<template>
  <ul class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3">
    <li v-for="form in forms" :key="form.id">
      <NuxtLink :to="{ name: 'form', params: { id: form.id } }">
        <FormCard :form="form" />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{
  forms: Form[];
}>();
</script>
