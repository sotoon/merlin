<template>
  <nav class="flex h-full w-64 flex-col overflow-hidden pb-4">
    <NuxtLink
      class="flex items-center justify-center gap-2 pb-2 pt-2 shadow"
      to="/"
    >
      <img src="/merlin.png" alt="Merlin" class="size-10" />
      <PText as="p" class="text-center" weight="bold" variant="subtitle">
        {{ t('common.appName') }}
      </PText>
    </NuxtLink>

    <div class="flex grow flex-col overflow-hidden px-2">
      <PScrollbar class="-mx-2 grow px-2 py-4">
        <ul class="space-y-2">
          <li>
            <SidebarLinkGroup
              id="sidebar-notes"
              guide-key="notes"
              :title="t('common.notes')"
              :is-active="isNotesGroupActive"
            >
              <li>
                <SidebarLink
                  id="sidebar-notes-goals"
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.goal]"
                  :label="t('common.goals')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.goal] },
                  }"
                  :is-active="isGoalActive"
                />
              </li>

              <li>
                <SidebarLink
                  id="sidebar-notes-forms"
                  icon="i-mdi-form"
                  :label="t('common.forms')"
                  :to="{ name: 'forms' }"
                  :is-active="isFormsActive"
                />
              </li>

              <li
                class="relative pr-8 before:absolute before:bottom-0 before:right-5 before:top-0 before:my-1 before:w-px before:bg-gray-20"
              >
                <SidebarLink
                  id="sidebar-notes-my-forms"
                  icon="i-mdi-chart-bar"
                  :label="t('common.results')"
                  :to="{ name: 'my-forms' }"
                  :is-active="isMyFormsActive"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup
              id="sidebar-promotion"
              guide-key="promotion"
              :title="t('common.promotion')"
              :is-active="isPromotionGroupActive"
            >
              <li>
                <SidebarLink
                  id="sidebar-promotion-promotion"
                  :icon="PROPOSAL_TYPE_ICON[PROPOSAL_TYPE.promotion]"
                  :label="t('proposalType.promotion')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
                    query: { proposal_type: PROPOSAL_TYPE.promotion },
                  }"
                  :is-active="isProposalActive(PROPOSAL_TYPE.promotion)"
                />
              </li>
              <!-- <li>
                <SidebarLink
                  :icon="PROPOSAL_TYPE_ICON[PROPOSAL_TYPE.notice]"
                  :label="t('proposalType.notice')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
                    query: { proposal_type: PROPOSAL_TYPE.notice },
                  }"
                  :is-active="isProposalActive(PROPOSAL_TYPE.notice)"
                />
              </li> -->
              <li>
                <SidebarLink
                  id="sidebar-promotion-mapping"
                  :icon="PROPOSAL_TYPE_ICON[PROPOSAL_TYPE.mapping]"
                  :label="t('proposalType.mapping')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
                    query: { proposal_type: PROPOSAL_TYPE.mapping },
                  }"
                  :is-active="isProposalActive(PROPOSAL_TYPE.mapping)"
                />
              </li>
              <li>
                <SidebarLink
                  id="sidebar-promotion-evaluation"
                  :icon="PROPOSAL_TYPE_ICON[PROPOSAL_TYPE.evaluation]"
                  :label="t('proposalType.evaluation')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
                    query: { proposal_type: PROPOSAL_TYPE.evaluation },
                  }"
                  :is-active="isProposalActive(PROPOSAL_TYPE.evaluation)"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup
              id="sidebar-feedback"
              guide-key="feedback"
              :has-badge="!!newFeedbackCount || !!newAdhocFeedbackCount"
              :title="t('common.feedback')"
              :is-active="isFeedbackGroupActive"
            >
              <li>
                <SidebarLink
                  id="sidebar-feedback-feedback-request"
                  :badge-count="newFeedbackCount"
                  icon="i-mdi-comment-check"
                  :label="t('common.feedbackRequest')"
                  :to="{ name: 'feedback' }"
                  :is-active="isFeedbackActive"
                />
              </li>
              <li>
                <SidebarLink
                  id="sidebar-feedback-adhoc-feedback"
                  :badge-count="newAdhocFeedbackCount"
                  icon="i-mdi-comment-quote-outline"
                  :label="t('feedback.adhocFeedback')"
                  :to="{ name: 'adhoc-feedback' }"
                  :is-active="isAdhocFeedbackActive"
                />
              </li>
              <!-- TODO: message is deprecated -->
              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.message]"
                  :label="t('noteType.message')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message] },
                  }"
                  :is-active="isMessageActive"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup
              id="sidebar-personal"
              guide-key="personal"
              :title="t('common.personal')"
              :is-active="isPersonalGroupActive"
              :guide-conditions="{
                showPerformanceTable:
                  !!profilePermissions?.ui_hints.show_performance_table,
              }"
            >
              <li>
                <SidebarLink
                  id="sidebar-personal-meetings"
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.meeting]"
                  :label="t('common.meetings')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.meeting] },
                  }"
                  :is-active="isMeetingActive"
                />
              </li>
              <li>
                <SidebarLink
                  id="sidebar-personal-templates"
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.template]"
                  :label="t('common.templates')"
                  :to="{ name: 'templates' }"
                  :is-active="isTemplatesActive"
                />
              </li>
              <li v-if="profilePermissions?.ui_hints.show_performance_table">
                <SidebarLink
                  id="sidebar-personal-performance-table"
                  icon="i-mdi-chart-line"
                  :label="t('common.performanceTable')"
                  :to="{ name: 'performance-list' }"
                  :is-active="isPerformanceTableActive"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup
              id="sidebar-my-team"
              guide-key="my-team"
              :has-badge="!!newOneOnOneCount"
              :title="t('common.myTeam')"
              :is-active="isMyTeamGroupActive"
              :guide-conditions="{ isTeamLeader: isTeamLeader }"
            >
              <li v-if="isTeamLeader">
                <SidebarLink
                  id="sidebar-my-team-my-team"
                  icon="i-mdi-account-group"
                  :label="t('common.myTeam')"
                  :to="{ name: 'my-team' }"
                  :is-active="isMyTeamActive"
                />
              </li>
              <li>
                <SidebarLink
                  id="sidebar-my-team-one-on-one"
                  :badge-count="newOneOnOneCount"
                  icon="i-mdi-account-supervisor"
                  :label="t('common.oneOnOne')"
                  :to="{ name: 'one-on-one' }"
                  :is-active="isOneOnOneActive"
                />
              </li>
            </SidebarLinkGroup>
          </li>
        </ul>
      </PScrollbar>

      <div class="flex flex-col space-y-2 border-t border-gray-10 pt-2">
        <SidebarLink
          id="sidebar-messages"
          :badge-count="newMessagesCount"
          icon="i-mdi-message-text"
          :label="t('common.messages')"
          :to="{ name: 'messages' }"
          :is-active="isMessagesActive"
          @click="startMessagesTour"
        />

        <SidebarLink
          id="sidebar-users"
          icon="i-mdi-account-group-outline"
          :label="t('common.users')"
          :to="{ name: 'user-list' }"
          :is-active="isUsersActive"
          @click="startUsersTour"
        />

        <SidebarProfileLink id="sidebar-profile" @click="startProfileTour" />
      </div>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';
import { SIDEBAR_TOUR_STEPS } from '~/constants/sidebarGuide';

const scrollbarRef = ref<HTMLElement>();
provide('scrollbarRef', scrollbarRef);

const closeGroupFns = new Map<string, () => void>();
const registerCloseGroup = (id: string, closeFn: () => void) => {
  closeGroupFns.set(id, closeFn);
};
const closeAllGroupsExcept = (exceptId: string) => {
  closeGroupFns.forEach((closeFn, id) => {
    if (id !== exceptId) {
      closeFn();
    }
  });
};
provide('registerCloseGroup', registerCloseGroup);
provide('closeAllGroupsExcept', closeAllGroupsExcept);

const { t } = useI18n();
const route = useRoute();
const { data: messages } = useGetNotes({
  retrieveMentions: true,
  justUnread: true,
  excludeContent: true,
});
const isTeamLeader = useIsTeamLeader();
const { data: profile } = useGetProfile();
const { data: profilePermissions } = useGetProfilePermissions();

const { start: startMessagesTour } = useIntro(
  SIDEBAR_TOUR_STEPS.messages || [],
  'sidebar-guide-messages',
);

const { start: startUsersTour } = useIntro(
  SIDEBAR_TOUR_STEPS.users || [],
  'sidebar-guide-users',
);

const { start: startProfileTour } = useIntro(
  SIDEBAR_TOUR_STEPS.profile || [],
  'sidebar-guide-profile',
);

const isProposalActive = (proposalType: ProposalType) => {
  return (
    route.name === 'notes' &&
    route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] &&
    route.query.proposal_type === proposalType
  );
};

const newMessagesCount = computed(
  () =>
    (messages.value || []).filter((message) => {
      if (
        message.type === NOTE_TYPE.template ||
        message.type === NOTE_TYPE.oneOnOne
      ) {
        return false;
      }
      if (
        message.type === NOTE_TYPE.feedbackRequest ||
        message.type === NOTE_TYPE.feedback
      ) {
        if (message.mentioned_users?.includes(profile.value?.email || '')) {
          return true;
        }
        return false;
      }
      return true;
    }).length,
);

const newFeedbackCount = computed(() => {
  const uniqueFeedbackRequestUuids = new Set<string>();
  (messages.value || []).forEach((message) => {
    if (
      message.type === NOTE_TYPE.feedback &&
      message.feedback_request_uuid_of_feedback
    ) {
      uniqueFeedbackRequestUuids.add(message.feedback_request_uuid_of_feedback);
    }

    if (message.type === NOTE_TYPE.feedbackRequest) {
      if (!message.mentioned_users?.includes(profile.value?.email || '')) {
        uniqueFeedbackRequestUuids.add(message.feedback_request_uuid || '');
      }
    }
  });

  return uniqueFeedbackRequestUuids.size;
});

const newAdhocFeedbackCount = computed(
  () =>
    (messages.value || []).filter(
      (message) =>
        message.type === NOTE_TYPE.feedback &&
        !message.feedback_request_uuid_of_feedback &&
        !message.mentioned_users?.includes(profile.value?.email || ''),
    ).length,
);

const newOneOnOneCount = computed(
  () =>
    (messages.value || []).filter(
      (message) => message.type === NOTE_TYPE.oneOnOne,
    ).length,
);

const isNotesGroupActive = computed(() => {
  return (
    (route.name === 'notes' && route.params.type === 'goal') ||
    route.name === 'forms' ||
    route.name === 'my-forms'
  );
});

const isPromotionGroupActive = computed(() => {
  return (
    route.name === 'notes' &&
    route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal]
  );
});

const isFeedbackGroupActive = computed(() => {
  return (
    route.name === 'feedback' ||
    route.name === 'adhoc-feedback' ||
    (route.name === 'notes' &&
      route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message])
  );
});

const isPersonalGroupActive = computed(() => {
  return (
    (route.name === 'notes' &&
      route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.meeting]) ||
    route.name === 'templates' ||
    route.name === 'performance-list'
  );
});

const isMyTeamGroupActive = computed(() => {
  return route.name === 'my-team' || route.name === 'one-on-one';
});

const isGoalActive = computed(() => {
  return (
    route.name === 'notes' &&
    route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.goal]
  );
});

const isFormsActive = computed(() => {
  return route.name === 'forms';
});

const isMyFormsActive = computed(() => {
  return route.name === 'my-forms';
});

const isFeedbackActive = computed(() => {
  return route.name === 'feedback';
});

const isAdhocFeedbackActive = computed(() => {
  return route.name === 'adhoc-feedback';
});

const isMessageActive = computed(() => {
  return (
    route.name === 'notes' &&
    route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message]
  );
});

const isMeetingActive = computed(() => {
  return (
    route.name === 'notes' &&
    route.params.type === NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.meeting]
  );
});

const isTemplatesActive = computed(() => {
  return route.name === 'templates';
});

const isPerformanceTableActive = computed(() => {
  return route.name === 'performance-list';
});

const isMyTeamActive = computed(() => {
  return route.name === 'my-team';
});

const isOneOnOneActive = computed(() => {
  return route.name === 'one-on-one';
});

const isMessagesActive = computed(() => {
  return route.name === 'messages';
});

const isUsersActive = computed(() => {
  return route.name === 'user-list';
});
</script>
