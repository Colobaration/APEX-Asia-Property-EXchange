/**
 * Хук для управления формами с валидацией
 */

import { useState, useCallback, useRef } from 'react';
import { z } from 'zod';
import { validateForm, validateField } from '@/lib/validation';

interface UseFormOptions<T> {
  initialValues: T;
  validationSchema?: z.ZodSchema<T>;
  onSubmit?: (data: T) => Promise<void> | void;
  onError?: (errors: Record<string, string>) => void;
}

interface FormState<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

export const useForm = <T extends Record<string, any>>({
  initialValues,
  validationSchema,
  onSubmit,
  onError,
}: UseFormOptions<T>) => {
  const [state, setState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true,
  });

  const formRef = useRef<HTMLFormElement>(null);

  // Обновление значений полей
  const setFieldValue = useCallback((field: keyof T, value: any) => {
    setState(prev => {
      const newValues = { ...prev.values, [field]: value };
      const newTouched = { ...prev.touched, [field]: true };
      
      // Валидация поля в реальном времени
      let newErrors = { ...prev.errors };
      if (validationSchema) {
        const fieldSchema = validationSchema.shape[field as string];
        if (fieldSchema) {
          const validation = validateField(fieldSchema, value);
          if (!validation.success) {
            newErrors[field as string] = validation.error;
          } else {
            delete newErrors[field as string];
          }
        }
      }

      return {
        ...prev,
        values: newValues,
        touched: newTouched,
        errors: newErrors,
        isValid: Object.keys(newErrors).length === 0,
      };
    });
  }, [validationSchema]);

  // Обработка изменения поля
  const handleChange = useCallback((field: keyof T) => (value: any) => {
    setFieldValue(field, value);
  }, [setFieldValue]);

  // Обработка blur события
  const handleBlur = useCallback((field: keyof T) => () => {
    setState(prev => ({
      ...prev,
      touched: { ...prev.touched, [field]: true },
    }));
  }, []);

  // Валидация всей формы
  const validateFormData = useCallback(() => {
    if (!validationSchema) return { success: true, errors: {} };

    const validation = validateForm(validationSchema, state.values);
    if (!validation.success) {
      setState(prev => ({
        ...prev,
        errors: validation.errors,
        isValid: false,
      }));
      onError?.(validation.errors);
    } else {
      setState(prev => ({
        ...prev,
        errors: {},
        isValid: true,
      }));
    }
    return validation;
  }, [validationSchema, state.values, onError]);

  // Отправка формы
  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault();

    setState(prev => ({ ...prev, isSubmitting: true }));

    try {
      // Валидация формы
      const validation = validateFormData();
      if (!validation.success) {
        return;
      }

      // Вызов onSubmit
      if (onSubmit) {
        await onSubmit(state.values);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setState(prev => ({
        ...prev,
        errors: { general: 'Ошибка отправки формы' },
      }));
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [state.values, validateFormData, onSubmit]);

  // Сброс формы
  const resetForm = useCallback(() => {
    setState({
      values: initialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
      isValid: true,
    });
  }, [initialValues]);

  // Установка ошибок
  const setErrors = useCallback((errors: Record<string, string>) => {
    setState(prev => ({
      ...prev,
      errors,
      isValid: Object.keys(errors).length === 0,
    }));
  }, []);

  // Установка значений
  const setValues = useCallback((values: Partial<T>) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, ...values },
    }));
  }, []);

  // Получение ошибки поля
  const getFieldError = useCallback((field: keyof T) => {
    return state.errors[field as string] || '';
  }, [state.errors]);

  // Проверка, было ли поле затронуто
  const isFieldTouched = useCallback((field: keyof T) => {
    return state.touched[field as string] || false;
  }, [state.touched]);

  // Проверка, есть ли ошибка у поля
  const hasFieldError = useCallback((field: keyof T) => {
    return !!state.errors[field as string];
  }, [state.errors]);

  // Создание пропсов для поля
  const getFieldProps = useCallback((field: keyof T) => ({
    value: state.values[field],
    onChange: handleChange(field),
    onBlur: handleBlur(field),
    error: getFieldError(field),
    hasError: hasFieldError(field),
    isTouched: isFieldTouched(field),
  }), [state.values, handleChange, handleBlur, getFieldError, hasFieldError, isFieldTouched]);

  return {
    // Состояние
    values: state.values,
    errors: state.errors,
    touched: state.touched,
    isSubmitting: state.isSubmitting,
    isValid: state.isValid,

    // Методы
    setFieldValue,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setErrors,
    setValues,
    validateFormData,

    // Утилиты
    getFieldError,
    isFieldTouched,
    hasFieldError,
    getFieldProps,

    // Ref для формы
    formRef,
  };
};
