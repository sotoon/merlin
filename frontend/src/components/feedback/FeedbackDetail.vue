<script lang="ts" setup>
import {
  PText,
  PTooltip,
  PIconButton,
  PInlineConfirm,
  PLoading,
} from '@pey/core';
import {
  PeyEditIcon,
  PeyTrashIcon,
  PeyCircleTickOutlineIcon,
  PeyCloseIcon,
} from '@pey/icons';

const props = defineProps<{
  request: Schema<'FeedbackRequestReadOnly'>;
  entries: Schema<'Feedback'>[];
}>();

const { t } = useI18n();
const { data: profile } = useGetProfile();
const { data: forms } = useGetFeedbackForms();
const { data: users } = useGetUsers();
const { mutateAsync: deleteRequest, isPending: isDeleting } =
  useDeleteFeedbackRequest(props.request.uuid);

function handleDelete() {
  deleteRequest(null).then(() => {
    navigateTo({ name: 'feedback' });
  });
}

const isOwner = computed(
  () => profile.value?.uuid === props.request.owner_uuid,
);
const canEdit = computed(() => isOwner.value && props.entries.length === 0);

const currentUserRequesteeLink = computed(() => {
  if (!profile.value) return null;
  return props.request.requestees.find((r) => r.uuid === profile.value?.uuid);
});

const canSubmitFeedback = computed(() => {
  return (
    currentUserRequesteeLink.value && !currentUserRequesteeLink.value.answered
  );
});

const formSchema = computed(() => {
  if (!props.request.form_uuid || !forms.value) return undefined;
  const form = forms.value.find((f) => f.uuid === props.request.form_uuid);
  return form?.schema as FeedbackFormSchema;
});

// Map mentioned user emails to user objects with names
const mentionedUsers = computed(() => {
  if (!props.request.note?.mentioned_users?.length || !users.value) return [];

  return props.request.note.mentioned_users
    .map((email) => {
      const user = users.value?.find((u) => u.email === email);
      return user ? { email, name: user.name } : { email, name: email };
    })
    .filter(Boolean);
});
</script>

<template>
  <div class="px-2 sm:px-4">
    <div class="flex items-start justify-between gap-8">
      <div>
        <i
          class="i-mdi-comment-quote-outline mb-3 me-4 inline-block align-middle text-h1 text-primary"
        />
        <PText responsive variant="h1" weight="bold">
          {{ request.title }}
        </PText>
      </div>

      <div v-if="canEdit" class="mt-2 flex items-center gap-4">
        <PIconButton
          class="shrink-0"
          :icon="PeyEditIcon"
          type="button"
          @click="
            navigateTo({
              name: 'feedback-edit',
              params: { requestId: request.uuid },
            })
          "
        />
        <PLoading v-if="isDeleting" class="text-primary" />
        <PInlineConfirm
          v-else
          :confirm-button-text="t('common.delete')"
          :message="t('feedback.confirmDelete')"
          @confirm="handleDelete"
        >
          <PIconButton
            :icon="PeyTrashIcon"
            color="danger"
            type="button"
            @click.prevent
          />
        </PInlineConfirm>
      </div>
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.lastEdit') }}:
        <PTooltip>
          <PText class="text-gray-70" variant="caption1">
            {{ formatTimeAgo(new Date(request.date_updated), 'fa-IR') }}
          </PText>
          <template #content>
            <PText dir="ltr" variant="caption1">
              {{ new Date(request.date_updated).toLocaleString('fa-IR') }}
            </PText>
          </template>
        </PTooltip>
      </PText>

      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.writer') }}:
        <span class="text-primary">
          {{ request.owner_name }}
        </span>
      </PText>
    </div>

    <div v-if="isOwner" class="mt-6">
      <PText as="p" class="mb-2 text-gray-50" variant="caption1">
        {{ t('feedback.requestees') }}:
      </PText>
      <div class="flex flex-wrap items-center gap-2">
        <div
          v-for="requestee in request.requestees"
          :key="requestee.uuid"
          class="flex items-center gap-x-1 rounded-full border border-gray-20 px-2 py-1"
        >
          <span>{{ requestee.name }}</span>
          <PTooltip>
            <component
              :is="requestee.answered ? PeyCircleTickOutlineIcon : PeyCloseIcon"
              class="h-4 w-4"
              :class="[requestee.answered ? 'text-success' : 'text-danger']"
            />
            <template #content>
              <PText variant="caption1">
                {{
                  requestee.answered
                    ? t('feedback.answered')
                    : t('feedback.notAnswered')
                }}
              </PText>
            </template>
          </PTooltip>
        </div>
      </div>
    </div>

    <div v-if="request.note?.mentioned_users?.length" class="mt-6">
      <PText as="p" class="mb-2 text-gray-50" variant="caption1">
        {{ t('note.mentionedUsers') }}:
      </PText>
      <div class="flex flex-wrap items-center gap-2">
        <div
          v-for="user in mentionedUsers"
          :key="user.email"
          class="rounded-full border border-gray-20 px-2 py-1"
        >
          <span>{{ user.name }}</span>
        </div>
      </div>
    </div>

    <article class="mt-4 py-4">
      <PText class="mb-2 text-gray-50" variant="caption1" weight="bold">
        {{ t('feedback.description') }}
      </PText>
      <EditorContent :content="request.content" />
    </article>

    <FeedbackResponseForm v-if="canSubmitFeedback" :request="request" />
    <FeedbackEntries v-else :entries="entries" :form-schema="formSchema" />
  </div>
</template>
