import type { RouteLocationRaw } from 'vue-router';

export interface SidebarLink {
  icon: string;
  label: string;
  to: RouteLocationRaw;
}

export const getNotesLinks = (t: (key: string) => string): SidebarLink[] => [
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.goal],
    label: t('common.goals'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.goal] },
    },
  },
];

export const getPromotionLinks = (
  t: (key: string) => string,
): SidebarLink[] => [
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.proposal],
    label: t('common.proposal'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
    },
  },
];

export const getFeedbackLinks = (t: (key: string) => string): SidebarLink[] => [
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.message],
    label: t('common.messageToOthers'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message] },
    },
  },
];
