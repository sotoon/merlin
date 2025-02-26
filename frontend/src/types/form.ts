export interface Question {
  id: number;
  question_text: string;
  scale_min: number;
  scale_max: number;
  category: string;
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
  cycle: number;
  cycle_name: string;
  cycle_start_date: string;
  cycle_end_date: string;
  assigned_by?: number;
  assigned_by_name?: string;
}

export interface FormDetails extends Omit<Form, 'assigned_by'> {
  questions: Question[];
  previous_responses: Record<string, string | null>;
  assigned_by: string | null;
}

export interface FormResponse {
  active_forms: Form[];
  expired_forms: Form[];
}

export interface FormResults {
  assigned_by: number;
  assigned_by_name: string;
  categories: Record<string, number>;
  questions: { id: number; average: number; text: string }[];
  total_average: number;
}
