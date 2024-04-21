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
  date_created: string;
  date_updated: string;
  mentioned_users: string[];
  owner: string;
  owner_name: string;
  period: number;
  read_status: boolean;
  title: string;
  type: NoteType;
  uuid: string;
  year: number;
}

export interface NoteFormValues
  extends Pick<
    Partial<Note>,
    'title' | 'content' | 'mentioned_users' | 'year'
  > {
  content: string;
  date?: Date;
  period?: number;
  title: string;
  year?: number;
}

export interface NoteSummary {
  bonus: number;
  committee_date: string;
  content: string;
  ladder_change: string;
  note: string;
  performance_label: string;
  salary_change: number;
  uuid: string;
}

export interface NoteSummaryFormValues extends Pick<NoteSummary, 'content'> {}

export interface NoteFeedback {
  content: string;
  note: string;
  owner: string;
  owner_name: string;
  uuid: string;
}

export interface NoteFeedbackFormValues {
  content: string;
}

export interface NoteTemplateFormValues
  extends Pick<Note, 'title' | 'content'> {}
