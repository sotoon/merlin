export const NOTE_TYPE = {
  goal: 'Goal',
  meeting: 'Meeting',
  message: 'Message',
  personal: 'Personal',
  proposal: 'Proposal',
  task: 'Task',
  template: 'Template',
} as const;

export const NOTE_TYPE_ROUTE_PARAM = {
  [NOTE_TYPE.goal]: 'goal',
  [NOTE_TYPE.meeting]: 'meeting',
  [NOTE_TYPE.message]: 'message',
  [NOTE_TYPE.personal]: 'personal',
  [NOTE_TYPE.proposal]: 'proposal',
  [NOTE_TYPE.task]: 'task',
} as const;

export const NOTE_TYPE_ICON = {
  [NOTE_TYPE.goal]: 'i-mdi-target-arrow',
  [NOTE_TYPE.meeting]: 'i-mdi-calendar',
  [NOTE_TYPE.message]: 'i-mdi-email-fast',
  [NOTE_TYPE.personal]: 'i-mdi-folder-lock',
  [NOTE_TYPE.proposal]: 'i-mdi-chart-line',
  [NOTE_TYPE.task]: 'i-mdi-check-circle',
  [NOTE_TYPE.template]: 'i-mdi-clipboard-text',
};

export const getNoteTypeLabels = (t: (key: string) => string) => ({
  [NOTE_TYPE.goal]: t('noteType.goal'),
  [NOTE_TYPE.meeting]: t('noteType.meeting'),
  [NOTE_TYPE.message]: t('noteType.message'),
  [NOTE_TYPE.personal]: t('noteType.personal'),
  [NOTE_TYPE.proposal]: t('noteType.proposal'),
  [NOTE_TYPE.task]: t('noteType.task'),
  [NOTE_TYPE.template]: t('noteType.template'),
});

export const NOTES_WITH_SUMMARY: NoteType[] = [
  NOTE_TYPE.goal,
  NOTE_TYPE.proposal,
];

export const PERFORMANCE_LABELS = [
  'نیاز به بهبود',
  'در حد انتظار',
  'فراتر از حد انتظار',
  'به طور ویژه‌ای فراتر از حد انتظار',
] as const;

export const SALARY_CHANGES = [0, 0.5, 1, 1.5, 2, 2.5, 3] as const;

export const NOTE_SORT_OPTION = {
  update: 'update',
  newest: 'newest',
  oldest: 'oldest',
  date: 'date',
  title: 'title',
} as const;

export const NOTE_SUBMIT_STATUS = {
  initial: 1,
  final: 2,
  reviewed: 3,
} as const;

export const NOTE_SUMMARY_SUBMIT_STATUS = {
  initial: 1,
  final: 2,
} as const;
