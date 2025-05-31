<template>
  <ul class="mt-4 grid grid-cols-1 gap-2 py-4 xl:grid-cols-2 xl:gap-3">
    <li v-for="form in forms" :key="form.id">
      <NuxtLink
        :to="
          assignedByMe
            ? {
                name: 'my-form',
                params: { id: form.id, userId: form.assigned_by || 0 },
              }
            : { name: 'form', params: { id: form.id } }
        "
      >
        <FormCard :form :display-assigned-by="displayAssignedBy" />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{
  forms: Form[];
  assignedByMe?: boolean;
  displayAssignedBy?: boolean;
}>();
</script>
