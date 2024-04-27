import type { RouteLocationRaw } from 'vue-router';

export interface SidebarLink {
  icon: string;
  label: string;
  to: RouteLocationRaw;
}

export const getNotesLinks = (t: (key: string) => string): SidebarLink[] => [
  {
    icon: '🚀',
    label: t('common.goals'),
    to: { name: 'notes', params: { type: 'goal' } },
  },
  {
    icon: '🛠️',
    label: t('common.tasks'),
    to: { name: 'notes', params: { type: 'task' } },
  },
  {
    icon: '🤝',
    label: t('common.meetings'),
    to: { name: 'notes', params: { type: 'meeting' } },
  },
  {
    icon: '📈',
    label: t('common.proposal'),
    to: { name: 'notes', params: { type: 'proposal' } },
  },
  {
    icon: '📨',
    label: t('common.messageToOthers'),
    to: { name: 'notes', params: { type: 'message' } },
  },
  {
    icon: '📝',
    label: t('common.personalNotes'),
    to: { name: 'notes', params: { type: 'personal' } },
  },
];
