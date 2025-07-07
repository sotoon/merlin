export type NoteType = (typeof NOTE_TYPE)[keyof typeof NOTE_TYPE];

export type NoteTypeRouteParam =
  (typeof NOTE_TYPE_ROUTE_PARAM)[keyof typeof NOTE_TYPE_ROUTE_PARAM];

export type NoteSubmitStatus =
  (typeof NOTE_SUBMIT_STATUS)[keyof typeof NOTE_SUBMIT_STATUS];

export type NoteSummarySubmitStatus =
  (typeof NOTE_SUMMARY_SUBMIT_STATUS)[keyof typeof NOTE_SUMMARY_SUBMIT_STATUS];

export interface Note {
  access_level: {
    can_edit: boolean;
    can_view: boolean;
    can_view_summary: boolean;
    can_write_feedback: boolean;
    can_write_summary: boolean;
  };
  content: string;
  date: string;
  date_created: string;
  date_updated: string;
  linked_notes: string[];
  mentioned_users: string[];
  owner: string;
  owner_name: string;
  period: number;
  read_status: boolean;
  submit_status: NoteSubmitStatus;
  title: string;
  type: NoteType;
  uuid: string;
  year: number;
  one_on_one_member: string | null;
  one_on_one_id: number | null;
  feedback_request_uuid: string | null;
}

export interface NoteFormValues
  extends Pick<
    Partial<Note>,
    'title' | 'content' | 'mentioned_users' | 'year' | 'period' | 'linked_notes'
  > {
  content: string;
  date?: Date;
  title: string;
}

export interface NoteSummary {
  bonus: number;
  committee_date: string | null;
  content: string;
  ladder_change: string;
  note: string;
  performance_label: string;
  salary_change: number;
  submit_status: NoteSummarySubmitStatus;
  uuid: string;
}

export interface NoteSummaryFormValues
  extends Pick<
    NoteSummary,
    | 'content'
    | 'performance_label'
    | 'ladder_change'
    | 'bonus'
    | 'salary_change'
  > {
  committee_date: Date;
}

export interface NoteTemplateFormValues
  extends Pick<Note, 'title' | 'content' | 'mentioned_users'> {}
