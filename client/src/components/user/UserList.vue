<template>
  <ul
    class="grid grid-cols-1 gap-2 py-4 md:grid-cols-2 md:gap-3 xl:grid-cols-3"
  >
    <li v-for="user in users" :key="user.uuid">
      <NuxtLink>
        <UserCard :user="user" />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{ users: User[] }>();
</script>
