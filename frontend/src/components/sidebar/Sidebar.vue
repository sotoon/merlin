<template>
  <nav class="flex h-full w-64 flex-col overflow-hidden pb-4">
    <NuxtLink class="pb-4 pt-2 shadow" to="/">
      <PText as="p" class="text-center" weight="bold" variant="h4">
        {{ t('common.appName') }}
      </PText>
    </NuxtLink>

    <div class="flex grow flex-col overflow-hidden px-2">
      <PScrollbar class="-mx-2 grow px-2 py-4">
        <ul class="space-y-2">
          <li>
            <SidebarLinkGroup :title="t('common.notes')">
              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.goal]"
                  :label="t('common.goals')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.goal] },
                  }"
                />
              </li>

              <li>
                <SidebarLink
                  icon="i-mdi-form"
                  :label="t('common.forms')"
                  :to="{ name: 'forms' }"
                />
              </li>

              <li
                class="relative pr-8 before:absolute before:bottom-0 before:right-5 before:top-0 before:my-1 before:w-px before:bg-gray-20"
              >
                <SidebarLink
                  icon="i-mdi-chart-bar"
                  :label="t('common.results')"
                  :to="{ name: 'my-forms' }"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup :title="t('common.promotion')">
              <li>
                <SidebarLink
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
              <li>
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
              </li>
              <li>
                <SidebarLink
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
              :has-badge="!!newFeedbackCount || !!newAdhocFeedbackCount"
              :title="t('common.feedback')"
            >
              <li>
                <SidebarLink
                  :badge-count="newFeedbackCount"
                  icon="i-mdi-comment-check"
                  :label="t('common.feedbackRequest')"
                  :to="{ name: 'feedback' }"
                />
              </li>
              <li>
                <SidebarLink
                  :badge-count="newAdhocFeedbackCount"
                  icon="i-mdi-comment-quote-outline"
                  :label="t('feedback.adhocFeedback')"
                  :to="{ name: 'adhoc-feedback' }"
                />
              </li>
              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.message]"
                  :label="t('noteType.message')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message] },
                  }"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup :title="t('common.personal')">
              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.meeting]"
                  :label="t('common.meetings')"
                  :to="{
                    name: 'notes',
                    params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.meeting] },
                  }"
                />
              </li>

              <li>
                <SidebarLink
                  :icon="NOTE_TYPE_ICON[NOTE_TYPE.template]"
                  :label="t('common.templates')"
                  :to="{ name: 'templates' }"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLinkGroup
              :has-badge="!!newOneOnOneCount"
              :title="t('common.myTeam')"
            >
              <li v-if="isTeamLeader">
                <SidebarLink
                  icon="i-mdi-account-group"
                  :label="t('common.myTeam')"
                  :to="{ name: 'my-team' }"
                />
              </li>
              <li>
                <SidebarLink
                  :badge-count="newOneOnOneCount"
                  icon="i-mdi-account-supervisor"
                  :label="t('common.oneOnOne')"
                  :to="{ name: 'one-on-one' }"
                />
              </li>
            </SidebarLinkGroup>
          </li>

          <li>
            <SidebarLink
              icon="i-mdi-account-group-outline"
              :label="t('common.users')"
              :to="{ name: 'user-list' }"
            />
          </li>
        </ul>
      </PScrollbar>

      <div class="flex flex-col space-y-2 border-t border-gray-10 pt-2">
        <SidebarLink
          :badge-count="newMessagesCount"
          icon="i-mdi-message-text"
          :label="t('common.messages')"
          :to="{ name: 'messages' }"
        />

        <SidebarLink
          icon="i-mdi-account-group-outline"
          :label="t('common.users')"
          :to="{ name: 'user-list' }"
        />

        <SidebarLink
          external
          icon="i-mdi-help-circle"
          :label="t('common.performanceManagementGuide')"
          :to="GUIDE_DRIVE_LINK"
        />

        <SidebarProfileLink />
      </div>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { PScrollbar, PText } from '@pey/core';

const { t } = useI18n();
const route = useRoute();
const { data: messages } = useGetNotes({ retrieveMentions: true });
const isTeamLeader = useIsTeamLeader();
const { data: profile } = useGetProfile();

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
      if (message.read_status) return false;
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
    if (message.read_status) return;

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
        !message.mentioned_users?.includes(profile.value?.email || '') &&
        !message.read_status,
    ).length,
);

const newOneOnOneCount = computed(
  () =>
    (messages.value || []).filter(
      (message) => message.type === NOTE_TYPE.oneOnOne && !message.read_status,
    ).length,
);
</script>
