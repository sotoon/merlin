<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<!-- eslint-disable vue/no-v-html -->
<template>
  <div>
    <div v-if="isEditMode">
      <PHeading class="mb-4 border-b border-gray-10 pb-4" level="h1" responsive>
        {{ note ? t('note.editNote') : t('note.newNote') }}
      </PHeading>

      <form class="space-y-4" @submit="onSubmit">
        <VeeField
          v-slot="{ componentField }"
          :label="t('note.title')"
          name="title"
          rules="required"
        >
          <PInput
            class="grow"
            v-bind="componentField"
            hide-details
            :label="t('note.title')"
            required
          />
        </VeeField>

        <VeeField v-slot="{ componentField }" name="content">
          <PInput
            v-bind="componentField"
            hide-details
            :rows="8"
            type="textarea"
          />
        </VeeField>

        <div class="flex items-center justify-end gap-4 pt-8">
          <PButton
            class="shrink-0"
            color="gray"
            type="button"
            variant="light"
            @click="handleCancel"
          >
            {{ t('common.cancel') }}
          </PButton>

          <PButton
            class="shrink-0"
            :disabled="!meta.valid"
            type="submit"
            variant="fill"
          >
            {{ t('common.save') }}
          </PButton>
        </div>
      </form>
    </div>

    <div v-else-if="note">
      <div class="flex items-center justify-between gap-4">
        <PHeading class="px-4" responsive>
          {{ note.title }}
        </PHeading>

        <PIconButton
          class="shrink-0"
          :icon="PeyEditIcon"
          type="button"
          @click="isEditMode = true"
        />
      </div>

      <div class="p-4" v-html="note.content" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { PButton, PHeading, PIconButton, PInput } from '@pey/core';
import { PeyEditIcon } from '@pey/icons';

const props = defineProps<{
  note?: Note;
}>();

const isEditMode = ref(!props.note);

const { t } = useI18n();
const router = useRouter();
const { meta, handleSubmit } = useForm({
  initialValues: { title: props.note?.title, content: props.note?.content },
  keepValuesOnUnmount: true,
});

const onSubmit = handleSubmit((values) => {
  console.log(values);
});

const handleCancel = () => {
  if (props.note) {
    isEditMode.value = false;
  } else {
    router.back();
  }
};
</script>
