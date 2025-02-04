export interface Question {
  id: number;
  question_text: string;
  scale_min: number;
  scale_max: number;
}

export type FormType = 'PM' | 'TL' | 'MANAGER' | 'GENERAL';

export interface Form {
  id: number;
  name: string;
  description: string;
  form_type: FormType | null;
  is_default: boolean;
  is_expired: boolean;
  is_filled: boolean;
}

export interface FormDetails extends Form {
  questions: Question[];
  previous_responses: Record<string, string | null>;
  assigned_by: string | null;
}

export interface FormResponse {
  active_forms: Form[];
  expired_forms: Form[];
}
