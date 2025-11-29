<script lang="ts" setup>
import { PBox, PHeading } from '@pey/core';
import type { SubmissionContext } from 'vee-validate';

definePageMeta({ name: 'one-on-one-edit' });
const props = defineProps<{
  oneOnOne: Schema<'OneOnOne'>;
  user: Schema<'Profile'>;
}>();

const { t } = useI18n();
const router = useRouter();

const { mutate: updateOneOnOne, isPending } = useUpdateOneOnOne({
  userId: props.user.uuid,
  oneOnOneId: props.oneOnOne.id,
});

// Type with corrected linked_notes (string[] instead of LinkedNoteRequest[])
type OneOnOneFormValues = Omit<Schema<'OneOnOneRequest'>, 'linked_notes'> & {
  linked_notes?: string[];
};

const handleSubmit = (
  values: OneOnOneFormValues,
  ctx: SubmissionContext<OneOnOneFormValues>,
) => {
  // Cast to Schema type for API call - the runtime values are compatible
  updateOneOnOne(values as Schema<'PatchedOneOnOneRequest'>, {
    onSuccess: () => {
      navigateTo({
        name: 'one-on-one-id',
        params: { userId: props.user.uuid, id: props.oneOnOne.id },
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
  <PBox class="mx-auto max-w-3xl border-none !shadow-none">
    <div class="mb-4 flex items-center gap-4 border-b border-gray-10 pb-4">
      <i class="i-mdi-calendar text-h1 text-primary" />

      <PHeading level="h1" responsive>
        {{ t('oneOnOne.editOneOnOne') }} {{ user ? `با ${user.name}` : '' }}
      </PHeading>
    </div>

    <NoteOneOnOneForm
      :one-on-one="oneOnOne"
      :user="user"
      :is-submitting="isPending"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PBox>
</template>
