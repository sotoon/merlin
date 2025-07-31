export type NoteType = (typeof NOTE_TYPE)[keyof typeof NOTE_TYPE];

export type NoteTypeRouteParam =
  (typeof NOTE_TYPE_ROUTE_PARAM)[keyof typeof NOTE_TYPE_ROUTE_PARAM];

export type ProposalType = (typeof PROPOSAL_TYPE)[keyof typeof PROPOSAL_TYPE];

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
  proposal_type?: ProposalType;
  uuid: string;
  year: number;
  one_on_one_member: string | null;
  one_on_one_id: number | null;
  feedback_request_uuid: string | null;
  feedback_uuid: string | null;
  feedback_request_uuid_of_feedback: string | null;
}

export interface NoteFormValues
  extends Pick<
    Partial<Note>,
    | 'title'
    | 'content'
    | 'mentioned_users'
    | 'year'
    | 'period'
    | 'linked_notes'
    | 'proposal_type'
  > {
  content: string;
  date?: Date;
  title: string;
}

export interface NoteTemplateFormValues
  extends Pick<Note, 'title' | 'content' | 'mentioned_users'> {}
