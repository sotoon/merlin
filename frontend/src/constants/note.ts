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

export const PERFORMANCE_BONUSES = [0, 5, 10, 15, 20] as const;

export const SALARY_CHANGES = [0, 0.5, 1, 1.5, 2, 2.5, 3] as const;

export const NOTE_SORT_OPTION = {
  update: 'update',
  period: 'period',
  date: 'date',
} as const;
