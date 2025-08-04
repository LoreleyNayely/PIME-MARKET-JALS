export interface FormField {
  value: string;
  error: string;
  touched: boolean;
}

export interface FormState {
  [key: string]: FormField;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: string) => string | null;
}
