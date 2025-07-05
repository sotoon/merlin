export const NOTE_TYPE = {
  goal: 'Goal',
  oneOnOne: 'OneOnOne',
  meeting: 'Meeting',
  message: 'Message',
  proposal: 'Proposal',
  template: 'Template',
  forms: 'forms',
} as const;

export const NOTE_TYPE_ROUTE_PARAM = {
  [NOTE_TYPE.goal]: 'goal',
  [NOTE_TYPE.oneOnOne]: 'oneOnOne',
  [NOTE_TYPE.meeting]: 'meeting',
  [NOTE_TYPE.message]: 'message',
  [NOTE_TYPE.proposal]: 'proposal',
  [NOTE_TYPE.forms]: 'forms',
} as const;

export const NOTE_TYPE_ICON = {
  [NOTE_TYPE.goal]: 'i-mdi-target-arrow',
  [NOTE_TYPE.oneOnOne]: 'i-mdi-calendar',
  [NOTE_TYPE.meeting]: 'i-mdi-calendar',
  [NOTE_TYPE.message]: 'i-mdi-email-fast',
  [NOTE_TYPE.proposal]: 'i-mdi-chart-line',
  [NOTE_TYPE.template]: 'i-mdi-clipboard-text',
  [NOTE_TYPE.forms]: 'i-mdi-form',
};

export const getNoteTypeLabels = (t: (key: string) => string) => ({
  [NOTE_TYPE.goal]: t('noteType.goal'),
  [NOTE_TYPE.oneOnOne]: t('noteType.oneOnOne'),
  [NOTE_TYPE.meeting]: t('noteType.meeting'),
  [NOTE_TYPE.message]: t('noteType.message'),
  [NOTE_TYPE.proposal]: t('noteType.proposal'),
  [NOTE_TYPE.template]: t('noteType.template'),
  [NOTE_TYPE.forms]: t('noteType.forms'),
});

export const NOTES_WITH_SUMMARY: NoteType[] = [
  NOTE_TYPE.goal,
  NOTE_TYPE.proposal,
];

export const EVALUATION_PERIODS = ['اول', 'دوم', 'سوم'] as const;

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
  period: 'period',
  date: 'date',
  title: 'title',
} as const;

export const ONE_ON_ONE_SORT_OPTION = {
  newest: 'newest',
  oldest: 'oldest',
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
