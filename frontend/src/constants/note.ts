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
