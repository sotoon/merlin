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
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.task],
    label: t('common.tasks'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.task] },
    },
  },
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.meeting],
    label: t('common.meetings'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.meeting] },
    },
  },
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.proposal],
    label: t('common.proposal'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.proposal] },
    },
  },
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.message],
    label: t('common.messageToOthers'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.message] },
    },
  },
  {
    icon: NOTE_TYPE_ICON[NOTE_TYPE.personal],
    label: t('common.personalNotes'),
    to: {
      name: 'notes',
      params: { type: NOTE_TYPE_ROUTE_PARAM[NOTE_TYPE.personal] },
    },
  },
];
