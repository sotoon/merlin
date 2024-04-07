<template>
  <ul
    class="grid grid-cols-1 gap-2 py-4 md:grid-cols-2 md:gap-3 xl:grid-cols-3"
  >
    <li v-for="user in users" :key="user.uuid">
      <NuxtLink
        :to="{
          name: 'notes',
          params: { type: 'user' },
          query: { email: user.email },
        }"
      >
        <UserCard :user="user" />
      </NuxtLink>
    </li>
  </ul>
</template>

<script lang="ts" setup>
defineProps<{ users: User[] }>();
</script>
