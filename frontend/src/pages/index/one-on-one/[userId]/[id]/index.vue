<script lang="ts" setup>
import {
  PChip,
  PHeading,
  PIconButton,
  PText,
  PTooltip,
  PDialog,
  PButton,
} from '@pey/core';
import {
  PeyEditIcon,
  PeyLinkIcon,
  PeyChevronLeftIcon,
  PeyChevronRightIcon,
} from '@pey/icons';
import dayjs from '~/utils/dayjs';

definePageMeta({ name: 'one-on-one-id' });

const props = defineProps<{ oneOnOne: Schema<'OneOnOne'>; user: User }>();
const { t } = useI18n();

const { data: myNotes } = useGetNotes();
const { data: mentionedNotes } = useGetNotes({ retrieveMentions: true });

// Get all one-on-ones for navigation (sorted by creation date on backend)
const { data: allOneOnOnes } = useGetOneOnOneList({
  userId: props.user.uuid,
  sort: ref('newest'),
});

// Find current index and get previous/next one-on-ones
const currentIndex = computed(
  () =>
    allOneOnOnes.value?.findIndex((item) => item.id === props.oneOnOne.id) ??
    -1,
);

const previousOneOnOne = computed(() => {
  const index = currentIndex.value;
  return index > 0 ? allOneOnOnes.value?.[index - 1] ?? null : null;
});

const nextOneOnOne = computed(() => {
  const index = currentIndex.value;
  return index >= 0 &&
    allOneOnOnes.value &&
    index < allOneOnOnes.value.length - 1
    ? allOneOnOnes.value[index + 1]
    : null;
});

const linkedNotes = computed(() => [
  ...(myNotes.value
    ?.filter(({ uuid }) =>
      (props.oneOnOne.note.linked_notes || []).includes(uuid),
    )
    .map((note) => ({
      ...note,
      to:
        note.type === NOTE_TYPE.template
          ? {
              name: 'template',
              params: { id: note.uuid },
            }
          : note.type === NOTE_TYPE.oneOnOne
            ? {
                name: 'one-on-one-id',
                params: {
                  userId: note.one_on_one_member,
                  id: note.one_on_one_id,
                },
              }
            : {
                name: 'note',
                params: {
                  type: NOTE_TYPE_ROUTE_PARAM[note.type],
                  id: note.uuid,
                },
              },
    })) || []),
  ...(mentionedNotes.value
    ?.filter(({ uuid }) =>
      (props.oneOnOne.note.linked_notes || []).includes(uuid),
    )
    .map((note) => ({
      ...note,
      to: {
        name: 'note',
        params: {
          type: '-',
          id: note.uuid,
        },
      },
    })) || []),
]);

const VIBES = [':)', ':|', ':('] as Schema<'MemberVibeEnum'>[];
const isTeamLeader = computed(() => props.oneOnOne.leader_vibe);
const isVibeModalOpen = ref(false);
const selectedVibe = ref<Schema<'MemberVibeEnum'>>();

const { mutate: updateOneOnOne, isPending } = useUpdateOneOnOne({
  userId: props.user.uuid,
  oneOnOneId: props.oneOnOne.id,
});

const handleVibeSubmit = () => {
  if (!selectedVibe.value) return;

  updateOneOnOne(
    { member_vibe: selectedVibe.value },
    {
      onSuccess: () => {
        isVibeModalOpen.value = false;
      },
    },
  );
};

function getRelatedTags(section: Schema<'SectionEnum'>) {
  return props.oneOnOne.tag_links.filter((tag) => tag.section === section);
}
</script>

<template>
  <div class="px-2 sm:px-4">
    <div class="flex items-start justify-between gap-8">
      <div>
        <i
          class="i-mdi-account-supervisor mb-3 me-4 inline-block align-middle text-h1 text-primary"
        />

        <PText responsive variant="h1" weight="bold">
          {{ oneOnOne.note.title }}
        </PText>
      </div>

      <div class="mt-2 flex items-end gap-4">
        <PButton
          v-if="previousOneOnOne"
          variant="light"
          size="small"
          @click="
            navigateTo({
              name: 'one-on-one-id',
              params: { userId: user.uuid, id: previousOneOnOne.id },
            })
          "
        >
          <PeyChevronRightIcon />
          جلسه
          {{
            dayjs(previousOneOnOne.date_created)
              .calendar('jalali')
              .locale('fa')
              .format('D MMMM')
          }}
        </PButton>

        <PButton
          v-if="nextOneOnOne"
          variant="light"
          size="small"
          @click="
            navigateTo({
              name: 'one-on-one-id',
              params: { userId: user.uuid, id: nextOneOnOne.id },
            })
          "
        >
          جلسه
          {{
            dayjs(nextOneOnOne.date_created)
              .calendar('jalali')
              .locale('fa')
              .format('D MMMM')
          }}
          <PeyChevronLeftIcon />
        </PButton>

        <PIconButton
          v-if="isTeamLeader"
          class="shrink-0"
          :icon="PeyEditIcon"
          type="button"
          @click="
            navigateTo({
              name: 'one-on-one-edit',
              params: { userId: user.uuid, id: oneOnOne.id },
            })
          "
        />
      </div>
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-4">
      <PChip
        v-if="isTeamLeader"
        :color="
          oneOnOne.leader_vibe === ':)'
            ? 'success'
            : oneOnOne.leader_vibe === ':('
              ? 'danger'
              : 'warning'
        "
        :label="getVibeEmoji(oneOnOne.leader_vibe)"
      />
      <PChip
        v-if="!isTeamLeader"
        :color="
          oneOnOne.member_vibe === ':)'
            ? 'success'
            : oneOnOne.member_vibe === ':('
              ? 'danger'
              : 'warning'
        "
        size="large"
        :label="`${getVibeEmoji(oneOnOne.member_vibe) || 'بازخوردی ثبت نشده است'}`"
      />

      <PButton
        v-if="!isTeamLeader && !oneOnOne.member_vibe"
        variant="light"
        @click="isVibeModalOpen = true"
      >
        {{ t('oneOnOne.submitVibe') }}
      </PButton>
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-4">
      <PText as="p" class="text-gray-50" variant="caption1">
        {{ t('note.lastEdit') }}:
        <PTooltip>
          <PText class="text-gray-70" variant="caption1">
            {{ formatTimeAgo(new Date(oneOnOne.date_updated || ''), 'fa-IR') }}
          </PText>

          <template #content>
            <PText dir="ltr" variant="caption1">
              {{
                new Date(oneOnOne.date_updated || '').toLocaleString('fa-IR')
              }}
            </PText>
          </template>
        </PTooltip>
      </PText>
    </div>

    <article class="mt-8 space-y-4 divide-y divide-gray-20">
      <div
        v-if="getRelatedTags('personal').length || oneOnOne.personal_summary"
        class="space-y-2"
      >
        <PHeading :lvl="4" responsive>
          {{ t('oneOnOne.individualDimension') }}
        </PHeading>
        <EditorContent :content="oneOnOne.personal_summary || '-'" />
        <div v-if="getRelatedTags('personal').length" class="mt-8">
          <div class="mt-4 flex flex-wrap gap-2">
            <PChip
              v-for="tag in getRelatedTags('personal')"
              :key="tag.id"
              :label="tag.tag.name_fa"
              color="primary"
              size="small"
            />
          </div>
        </div>
      </div>

      <div
        v-if="getRelatedTags('career').length || oneOnOne.career_summary"
        class="space-y-2 pt-4"
      >
        <PHeading :lvl="4" responsive>{{ t('oneOnOne.growthPath') }}</PHeading>
        <EditorContent :content="oneOnOne.career_summary || '-'" />
        <div v-if="getRelatedTags('career').length" class="mt-8">
          <div class="mt-4 flex flex-wrap gap-2">
            <PChip
              v-for="tag in getRelatedTags('career')"
              :key="tag.id"
              :label="tag.tag.name_fa"
              color="primary"
              size="small"
            />
          </div>
        </div>
      </div>

      <div
        v-if="
          getRelatedTags('communication').length ||
          oneOnOne.communication_summary
        "
        class="space-y-2 pt-4"
      >
        <PHeading :lvl="4" responsive>
          {{ t('oneOnOne.interactionAndCustomerOrientation') }}
        </PHeading>
        <EditorContent :content="oneOnOne.communication_summary || '-'" />
        <div v-if="getRelatedTags('communication').length" class="mt-8">
          <div class="mt-4 flex flex-wrap gap-2">
            <PChip
              v-for="tag in getRelatedTags('communication')"
              :key="tag.id"
              :label="tag.tag.name_fa"
              color="primary"
              size="small"
            />
          </div>
        </div>
      </div>

      <div class="space-y-2 pt-4">
        <PHeading :lvl="4" responsive>
          {{ t('oneOnOne.performanceManagement') }}
        </PHeading>
        <EditorContent :content="oneOnOne.performance_summary" />
        <div v-if="getRelatedTags('performance').length" class="mt-8">
          <div class="mt-4 flex flex-wrap gap-2">
            <PChip
              v-for="tag in getRelatedTags('performance')"
              :key="tag.id"
              :label="tag.tag.name_fa"
              color="primary"
              size="small"
            />
          </div>
        </div>
      </div>

      <div v-if="oneOnOne.actions" class="space-y-2 pt-4">
        <PHeading :lvl="4" responsive>
          {{ t('oneOnOne.whatActionsWeDefined') }}
        </PHeading>
        <EditorContent :content="oneOnOne.actions" />
      </div>

      <div v-if="oneOnOne.extra_notes" class="space-y-2 pt-4">
        <PHeading :lvl="4" responsive>
          {{ t('oneOnOne.additionalNotes') }}
        </PHeading>
        <EditorContent :content="oneOnOne.extra_notes || '-'" />
      </div>
    </article>

    <div v-if="linkedNotes?.length" class="mt-8">
      <PHeading :lvl="4" responsive>{{ t('note.relatedNotes') }}</PHeading>
      <div class="mt-4 flex flex-wrap gap-2">
        <NuxtLink
          v-for="linkedNote in linkedNotes"
          :key="linkedNote.uuid"
          class="*:cursor-pointer"
          :to="linkedNote.to"
        >
          <PChip
            color="primary"
            :icon="PeyLinkIcon"
            :label="linkedNote.title"
            size="small"
          />
        </NuxtLink>
      </div>
    </div>

    <PDialog
      v-model="isVibeModalOpen"
      :title="t('oneOnOne.submitVibe')"
      :loading="isPending"
    >
      <template #default>
        <PText>
          {{ t('oneOnOne.howWasTheMeetingVibeMember') }}
        </PText>

        <div class="mt-6 flex flex-wrap items-center justify-center gap-4">
          <button
            v-for="vibe in VIBES"
            :key="vibe"
            type="button"
            class="rounded-xl border-2 p-3 py-2 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            :class="[
              selectedVibe === vibe
                ? 'border-primary bg-primary/10'
                : 'border-gray-300 hover:border-gray-400',
              isPending ? 'cursor-not-allowed opacity-50' : '',
            ]"
            :disabled="isPending"
            @click="selectedVibe = vibe"
          >
            {{ getVibeEmoji(vibe) }}
          </button>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-4">
          <PButton
            variant="light"
            :disabled="isPending"
            @click="isVibeModalOpen = false"
          >
            {{ t('common.cancel') }}
          </PButton>
          <PButton
            variant="fill"
            :disabled="!selectedVibe || isPending"
            :loading="isPending"
            @click="handleVibeSubmit"
          >
            {{ t('common.submit') }}
          </PButton>
        </div>
      </template>
    </PDialog>

    <div class="mt-8">
      <NoteFeedbacks is-one-on-one :note="oneOnOne.note" />
    </div>
  </div>
</template>
