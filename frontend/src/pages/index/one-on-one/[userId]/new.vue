<script lang="ts" setup>
import { PBox, PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'one-on-one-new' });

const props = defineProps<{ user: User }>();

const { t } = useI18n();
const router = useRouter();

const { mutate: createOneOnOne, isPending } = useCreateOneOnOne({
  userId: props.user.uuid,
});

const handleSubmit = (
  values: Schema<'OneOnOneRequest'>,
  ctx: SubmissionContext<Schema<'OneOnOneRequest'>>,
) => {
  createOneOnOne(values, {
    onSuccess: () => {
      navigateTo({
        name: 'one-on-one-userId',
        params: { userId: props.user.uuid },
      });
      ctx.resetForm();
    },
  });
};

const handleCancel = () => {
  router.back();
};
</script>

<template>
  <PBox class="mx-auto max-w-3xl bg-white px-4 py-8 lg:px-8 lg:pt-10">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-calendar text-h1 text-primary" />

      <PHeading level="h1" responsive>
        {{ t('oneOnOne.createOneOnOne') }} {{ user ? `با ${user.name}` : '' }}
      </PHeading>
    </div>

    <NoteOneOnOneForm
      :user="user"
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>
