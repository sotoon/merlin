export interface SchemaQuestion {
  title: string;
  type: 'text' | 'tag' | 'select';
  options?: Array<{
    title: string;
    value: string;
  }>;
}
