<template>
  <NuxtPage :type="feedbackType || undefined" />
</template>

<script lang="ts" setup>
const route = useRoute();

const feedbackType = computed(() => {
  if (
    typeof route.params.type === 'string' &&
    (Object.values(FEEDBACK_TYPE) as string[]).includes(route.params.type)
  ) {
    return route.params.type;
  }

  return null;
});

onMounted(() => {
  if (feedbackType.value) {
    return;
  }

  navigateTo({
    name: 'feedbacks',
    params: { type: FEEDBACK_TYPE.Send },
    replace: true,
  });
});
</script>
