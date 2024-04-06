export type NoteType = (typeof NOTE_TYPE)[keyof typeof NOTE_TYPE];

export type NoteTypeRouteParam =
  (typeof NOTE_TYPE_ROUTE_PARAM)[keyof typeof NOTE_TYPE_ROUTE_PARAM];

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
  extends Pick<Partial<Note>, 'title' | 'content' | 'mentioned_users'> {
  content: string;
  title: string;
}

export interface NoteSummaryFormValues extends Pick<Note, 'summary'> {}

export interface NoteFeedback {
  content: string;
  note: string;
  owner: string;
  owner_name: string;
  uuid: string;
}
