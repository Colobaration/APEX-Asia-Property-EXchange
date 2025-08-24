/**
 * Система валидации форм с Zod
 */

import { z } from 'zod';

// Базовые схемы валидации
export const emailSchema = z
  .string()
  .min(1, 'Email обязателен')
  .email('Неверный формат email');

export const passwordSchema = z
  .string()
  .min(8, 'Пароль должен содержать минимум 8 символов')
  .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Пароль должен содержать буквы и цифры');

export const phoneSchema = z
  .string()
  .regex(/^\+?[1-9]\d{1,14}$/, 'Неверный формат телефона')
  .optional();

// Схемы для аутентификации
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Пароль обязателен'),
});

export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  confirm_password: z.string().min(1, 'Подтверждение пароля обязательно'),
  full_name: z.string().min(2, 'Имя должно содержать минимум 2 символа').optional(),
}).refine((data) => data.password === data.confirm_password, {
  message: 'Пароли не совпадают',
  path: ['confirm_password'],
});

export const profileUpdateSchema = z.object({
  email: emailSchema.optional(),
  full_name: z.string().min(2, 'Имя должно содержать минимум 2 символа').optional(),
  current_password: z.string().min(1, 'Текущий пароль обязателен').optional(),
  new_password: passwordSchema.optional(),
  confirm_new_password: z.string().optional(),
}).refine((data) => {
  if (data.new_password && !data.current_password) {
    return false;
  }
  return true;
}, {
  message: 'Текущий пароль обязателен для смены пароля',
  path: ['current_password'],
}).refine((data) => {
  if (data.new_password && data.confirm_new_password) {
    return data.new_password === data.confirm_new_password;
  }
  return true;
}, {
  message: 'Новые пароли не совпадают',
  path: ['confirm_new_password'],
});

// Схемы для лидов
export const leadSchema = z.object({
  first_name: z.string().min(2, 'Имя должно содержать минимум 2 символа'),
  last_name: z.string().min(2, 'Фамилия должна содержать минимум 2 символа'),
  email: emailSchema,
  phone: phoneSchema,
  company: z.string().min(1, 'Компания обязательна').optional(),
  position: z.string().min(1, 'Должность обязательна').optional(),
  source: z.enum(['website', 'referral', 'social_media', 'email', 'phone', 'other']),
  status: z.enum(['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']),
  notes: z.string().max(1000, 'Заметки не должны превышать 1000 символов').optional(),
  budget: z.number().min(0, 'Бюджет не может быть отрицательным').optional(),
  timeline: z.string().min(1, 'Сроки обязательны').optional(),
});

export const leadUpdateSchema = leadSchema.partial();

// Схемы для фильтров
export const leadFilterSchema = z.object({
  status: z.enum(['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']).optional(),
  source: z.enum(['website', 'referral', 'social_media', 'email', 'phone', 'other']).optional(),
  assigned_to: z.number().positive().optional(),
  created_after: z.string().datetime().optional(),
  created_before: z.string().datetime().optional(),
  search: z.string().min(1, 'Поисковый запрос не может быть пустым').optional(),
});

// Схемы для уведомлений
export const notificationSchema = z.object({
  title: z.string().min(1, 'Заголовок обязателен').max(200, 'Заголовок не должен превышать 200 символов'),
  message: z.string().min(1, 'Сообщение обязательно').max(1000, 'Сообщение не должно превышать 1000 символов'),
  notification_type: z.enum(['email', 'telegram', 'whatsapp', 'push', 'sms']),
  priority: z.enum(['low', 'normal', 'high', 'urgent']),
  recipient_email: emailSchema.optional(),
  recipient_phone: phoneSchema.optional(),
  recipient_telegram_id: z.string().min(1, 'Telegram ID обязателен').optional(),
});

// Схемы для аналитики
export const analyticsFilterSchema = z.object({
  date_range: z.object({
    start_date: z.string().datetime(),
    end_date: z.string().datetime(),
  }).optional(),
  user_id: z.number().positive().optional(),
  lead_source: z.string().optional(),
  lead_status: z.string().optional(),
});

// Утилиты для валидации
export const validateForm = <T>(schema: z.ZodSchema<T>, data: unknown): { success: true; data: T } | { success: false; errors: Record<string, string> } => {
  try {
    const validatedData = schema.parse(data);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {};
      (error as any).errors.forEach((err: any) => {
        const path = err.path.join('.');
        errors[path] = err.message;
      });
      return { success: false, errors };
    }
    return { success: false, errors: { general: 'Ошибка валидации' } };
  }
};

export const validateField = <T>(schema: z.ZodSchema<T>, value: unknown): { success: true; data: T } | { success: false; error: string } => {
  try {
    const validatedData = schema.parse(value);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, error: (error as any).errors[0]?.message || 'Ошибка валидации' };
    }
    return { success: false, error: 'Ошибка валидации' };
  }
};

// Хуки для валидации в реальном времени
export const useFieldValidation = <T>(schema: z.ZodSchema<T>) => {
  const validate = (value: unknown) => validateField(schema, value);
  return { validate };
};

// Типы для TypeScript
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ProfileUpdateData = z.infer<typeof profileUpdateSchema>;
export type LeadFormData = z.infer<typeof leadSchema>;
export type LeadUpdateData = z.infer<typeof leadUpdateSchema>;
export type LeadFilterData = z.infer<typeof leadFilterSchema>;
export type NotificationFormData = z.infer<typeof notificationSchema>;
export type AnalyticsFilterData = z.infer<typeof analyticsFilterSchema>;
