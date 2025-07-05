<template>
  <PInput
    v-model="inputValue"
    hide-details
    :placeholder="t('common.search')"
    size="small"
    type="search"
  >
    <template #iconStart>
      <PeySearchIcon class="text-gray-50" :size="20" />
    </template>
  </PInput>
</template>

<script lang="ts" setup>
import { PInput } from '@pey/core';
import { PeySearchIcon } from '@pey/icons';
import { debounce } from 'vue-debounce';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

// Local input value for immediate UI feedback
const inputValue = ref('');

// Initialize input value from URL query
onMounted(() => {
  inputValue.value = (route.query.q as string) || '';
});

// Debounced function to update URL
const updateURL = debounce((value: string) => {
  const query = { ...route.query };
  if (value) {
    query.q = value;
  } else {
    delete query.q;
  }
  router.replace({ query });
}, 300);

// Watch input value and debounce URL updates
watch(inputValue, (newValue) => {
  updateURL(newValue);
});

// Watch URL changes and update input value
watch(
  () => route.query.q,
  (newValue) => {
    if (newValue !== inputValue.value) {
      inputValue.value = (newValue as string) || '';
    }
  },
);
</script>
