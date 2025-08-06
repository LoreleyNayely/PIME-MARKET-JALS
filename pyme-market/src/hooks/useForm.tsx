import { useState, useCallback } from 'react';
import type { FormState, ValidationRule } from '../interfaces/forms';
import { ValidationService } from '../services/validationService';

interface UseFormOptions {
  initialValues: Record<string, string>;
  validationRules?: Record<string, ValidationRule>;
  onSubmit: (values: Record<string, string>) => Promise<void>;
}

export function useForm({ initialValues, validationRules = {}, onSubmit }: UseFormOptions) {
  const [formState, setFormState] = useState<FormState>(() => {
    const state: FormState = {};
    for (const key in initialValues) {
      state[key] = {
        value: initialValues[key],
        error: '',
        touched: false,
      };
    }
    return state;
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateField = useCallback((name: string, value: string): string => {
    const rules = validationRules[name];
    if (!rules) return '';

    return ValidationService.validateField(value, rules) || '';
  }, [validationRules]);

  const setFieldValue = useCallback((name: string, value: string) => {
    setFormState(prev => ({
      ...prev,
      [name]: {
        ...prev[name],
        value,
        error: validateField(name, value),
        touched: true,
      },
    }));
  }, [validateField]);

  const setFieldTouched = useCallback((name: string, touched = true) => {
    setFormState(prev => ({
      ...prev,
      [name]: {
        ...prev[name],
        touched,
        error: touched ? validateField(name, prev[name].value) : '',
      },
    }));
  }, [validateField]);

  const validateForm = useCallback((): boolean => {
    let isValid = true;
    const newFormState = { ...formState };

    for (const fieldName in formState) {
      const error = validateField(fieldName, formState[fieldName].value);
      newFormState[fieldName] = {
        ...newFormState[fieldName],
        error,
        touched: true,
      };
      if (error) {
        isValid = false;
      }
    }

    setFormState(newFormState);
    return isValid;
  }, [formState, validateField]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const values: Record<string, string> = {};
      for (const key in formState) {
        values[key] = formState[key].value;
      }
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [formState, validateForm, onSubmit]);

  const resetForm = useCallback(() => {
    const state: FormState = {};
    for (const key in initialValues) {
      state[key] = {
        value: initialValues[key],
        error: '',
        touched: false,
      };
    }
    setFormState(state);
  }, [initialValues]);

  const getFieldProps = useCallback((name: string) => ({
    value: formState[name]?.value || '',
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setFieldValue(name, e.target.value),
    onBlur: () => setFieldTouched(name),
    error: formState[name]?.error || '',
    touched: formState[name]?.touched || false,
  }), [formState, setFieldValue, setFieldTouched]);

  return {
    formState,
    isSubmitting,
    setFieldValue,
    setFieldTouched,
    handleSubmit,
    resetForm,
    getFieldProps,
    validateForm,
  };
}
