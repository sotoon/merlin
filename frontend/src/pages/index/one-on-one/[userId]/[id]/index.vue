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
  PeyInfoFilledIcon,
} from '@pey/icons';
import dayjs from '~/utils/dayjs';

definePageMeta({ name: 'one-on-one-id' });

const props = defineProps<{ oneOnOne: Schema<'OneOnOne'>; user: User }>();
const { t } = useI18n();

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

function getNoteRoute(note: Schema<'LinkedNote'>) {
  switch (note.type) {
    case NOTE_TYPE.template:
      return {
        name: 'template',
        params: { id: note.uuid },
      };
    case NOTE_TYPE.oneOnOne:
      return {
        name: 'one-on-one-id',
        params: {
          userId: note.one_on_one_member,
          id: note.one_on_one_id,
        },
      };
    case NOTE_TYPE.feedbackRequest:
      return {
        name: 'feedback-detail',
        params: { requestId: note.feedback_request_uuid },
      };
    case NOTE_TYPE.feedback:
      return {
        name: 'adhoc-feedback-detail',
        params: { id: note.feedback_uuid },
      };
    default:
      return {
        name: 'note',
        params: {
          type: NOTE_TYPE_ROUTE_PARAM[
            note.type as keyof typeof NOTE_TYPE_ROUTE_PARAM
          ],
          id: note.uuid,
        },
      };
  }
}

const linkedNotes = computed(() => {
  return (props.oneOnOne.note.linked_notes ?? []).map((note) => ({
    ...note,
    to: getNoteRoute(note),
  }));
});

const VIBES = [':)', ':|', ':('] as Schema<'MemberVibeEnum'>[];
const isTeamLeader = computed(() => props.oneOnOne.leader_vibe);
const isVibeModalOpen = ref(false);
const selectedVibe = ref<Schema<'MemberVibeEnum'>>();

// Tooltip visibility state
let infoTooltipTimeout: NodeJS.Timeout | null = null;
const infoTooltipVisibility = ref(false);

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

function hasUserDismissedInfoTooltip() {
  if (process.client) {
    return localStorage.getItem('one-on-one-info-tooltip-dismissed') === 'true';
  }
  return false;
}

function dismissInfoTooltip() {
  if (process.client) {
    localStorage.setItem('one-on-one-info-tooltip-dismissed', 'true');
  }
  infoTooltipVisibility.value = false;
}

onMounted(() => {
  if (!hasUserDismissedInfoTooltip()) {
    infoTooltipTimeout = setTimeout(() => {
      infoTooltipVisibility.value = true;

      infoTooltipTimeout = setTimeout(() => {
        infoTooltipVisibility.value = false;
      }, 5000);
    }, 1000);
  }
});

onBeforeUnmount(() => {
  infoTooltipTimeout && clearTimeout(infoTooltipTimeout);
});
</script>

<template>
  <div class="px-2 sm:px-4">
    <div class="flex items-start justify-between gap-8">
      <div class="flex items-center">
        <i
          class="i-mdi-account-supervisor mb-3 me-4 inline-block align-middle text-h1 text-primary"
        />

        <PText responsive variant="h1" weight="bold">
          {{ oneOnOne.note.title }}
        </PText>

        <PTooltip
          :model-value="infoTooltipVisibility"
          placement="bottom"
          @update:model-value="
            (value) => {
              if (!value) {
                dismissInfoTooltip();
              }
            }
          "
        >
          <PeyInfoFilledIcon class="mr-2 text-gray-50" />

          <template #content>
            <PText variant="caption1">
              اکثر اطلاعات موجود در یک‌به‌یک‌، فقط برای لیدر و عضو تیم قابل
              دسترسی هستن.
            </PText>
            <br />
            <PText variant="caption1">
              تنها سه بخش زیر توسط اچ‌آر برای بررسی و تحلیل استفاده می‌شن:
            </PText>
            <ul>
              <li>
                <PText variant="caption1">
                  ۱- متن موجود در بخش «مدیریت عملکرد»
                </PText>
              </li>
              <li>
                <PText variant="caption1">
                  ۲- تمامی تگ‌های انتخاب شده در بخش‌های مختلف (بدون جزئیات متون)
                </PText>
              </li>
              <li>
                <PText variant="caption1">
                  ۳- وایب‌ ایموجی‌هایی که لیدر و عضو تیم وارد می‌کنن
                </PText>
              </li>
            </ul>
            <br />
            <PText variant="caption1">
              به جز این سه دسته، اچ‌آر به باقی اطلاعاتی که در یک‌به‌یک وارد
              می‌کنید، دسترسی نداره.
            </PText>
            <br />
            <br />
            <PText variant="caption1">
              نکته: وایب وارد شده توسط هر فرد فقط برای خودش و اچ‌آر قابل
              مشاهده‌ست، <br />
              یعنی؛ لیدر دسترسی مشاهده‌ی ایموجی عضو تیم رو نداره، و بلعکس.
            </PText>
          </template>
        </PTooltip>
      </div>

      <div class="mt-2 flex items-end">
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
        v-if="!isTeamLeader"
        variant="light"
        @click="isVibeModalOpen = true"
      >
        {{
          oneOnOne.member_vibe
            ? t('oneOnOne.updateVibe')
            : t('oneOnOne.submitVibe')
        }}
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

    <div class="mt-8 flex justify-between">
      <PButton
        :class="!previousOneOnOne ? 'invisible' : ''"
        variant="light"
        size="small"
        @click="
          previousOneOnOne &&
            navigateTo({
              name: 'one-on-one-id',
              params: { userId: user.uuid, id: previousOneOnOne.id },
            })
        "
      >
        <PeyChevronRightIcon />
        جلسه
        {{
          previousOneOnOne
            ? dayjs(previousOneOnOne.date_created)
                .calendar('jalali')
                .locale('fa')
                .format('D MMMM')
            : ''
        }}
      </PButton>

      <PButton
        :class="!nextOneOnOne ? 'invisible' : ''"
        variant="light"
        size="small"
        @click="
          nextOneOnOne &&
            navigateTo({
              name: 'one-on-one-id',
              params: { userId: user.uuid, id: nextOneOnOne.id },
            })
        "
      >
        جلسه
        {{
          nextOneOnOne
            ? dayjs(nextOneOnOne.date_created)
                .calendar('jalali')
                .locale('fa')
                .format('D MMMM')
            : ''
        }}
        <PeyChevronLeftIcon />
      </PButton>
    </div>

    <div class="mt-8">
      <NoteComments :note="oneOnOne.note" type="one-on-one" />
    </div>
  </div>
</template>
