export const NOTE_TYPE = {
  goal: 'Goal',
  meeting: 'Meeting',
  message: 'Message',
  personal: 'Personal',
  proposal: 'Proposal',
  task: 'Task',
  template: 'Template',
} as const;

export type NoteType = (typeof NOTE_TYPE)[keyof typeof NOTE_TYPE];

export interface Note {
  access_level: {
    can_edit: boolean;
    can_view: boolean;
    can_write_feedback: boolean;
    can_write_summary: boolean;
  };
  content: string;
  date: string;
  mentioned_users: string[];
  owner: string;
  owner_name: string;
  read_status: boolean;
  summary: string;
  title: string;
  type: NoteType;
  uuid: string;
}

export interface NoteFormValues
  extends Pick<Partial<Note>, 'title' | 'content'> {
  content: string;
  title: string;
}
