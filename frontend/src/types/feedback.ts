interface SchemaQuestion {
  key: string;
  type: 'text' | 'likert' | 'tag' | 'multiple_choice' | 'sort';
  title: string;
  helpText?: string;
  required: boolean;
  placeholder?: string;
  options?: {
    value: string;
    label: string;
  }[];
  scale?: {
    min: number;
    max: number;
    labels: Record<string, string>;
  };
  default?: any;
  defaultOrder?: string[];
}

interface SchemaSection {
  key: string;
  title: string;
  items: SchemaQuestion[];
}

export interface FeedbackFormSchema {
  sections: SchemaSection[];
}
