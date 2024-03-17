export interface SidebarLink {
  icon: string;
  label: string;
  to: string;
}

export interface SidebarLinkGroup {
  title: string;
  links: SidebarLink[];
}

const getSidebarLinks = (t: (key: string) => string) =>
  [
    {
      title: t('common.notes'),
      links: [
        { icon: '🚀', label: t('common.goals'), to: '/notes/goal' },
        { icon: '🤝', label: t('common.meetings'), to: '/notes/meeting' },
        { icon: '📝', label: t('common.personalNotes'), to: '/notes/personal' },
        { icon: '🛠️', label: t('common.tasks'), to: '/notes/task' },
        { icon: '📈', label: t('common.proposal'), to: '/notes/proposal' },
        {
          icon: '📨',
          label: t('common.messageToOthers'),
          to: '/notes/message',
        },
      ],
    },
    {
      title: t('common.personal'),
      links: [
        { icon: '💬', label: t('common.messages'), to: '/messages' },
        { icon: '📋', label: t('common.templates'), to: '/templates' },
      ],
    },
  ] satisfies SidebarLinkGroup[];

export default getSidebarLinks;
