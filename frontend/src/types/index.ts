/**
 * Основные TypeScript типы для APEX
 */

// Типы пользователей
export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

// Типы лидов
export enum LeadStatus {
  NEW = 'new',
  CONTACTED = 'contacted',
  QUALIFIED = 'qualified',
  PROPOSAL = 'proposal',
  NEGOTIATION = 'negotiation',
  CLOSED_WON = 'closed_won',
  CLOSED_LOST = 'closed_lost',
}

export enum LeadSource {
  WEBSITE = 'website',
  REFERRAL = 'referral',
  SOCIAL_MEDIA = 'social_media',
  EMAIL = 'email',
  PHONE = 'phone',
  OTHER = 'other',
}

export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  position?: string;
  source: LeadSource;
  status: LeadStatus;
  notes?: string;
  budget?: number;
  timeline?: string;
  amo_crm_id?: number;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
}

// Типы уведомлений
export enum NotificationType {
  EMAIL = 'email',
  TELEGRAM = 'telegram',
  WHATSAPP = 'whatsapp',
  PUSH = 'push',
  SMS = 'sms',
}

export enum NotificationStatus {
  PENDING = 'pending',
  SENT = 'sent',
  FAILED = 'failed',
  DELIVERED = 'delivered',
  READ = 'read',
}

export enum NotificationPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: NotificationType;
  priority: NotificationPriority;
  status: NotificationStatus;
  recipient_email?: string;
  recipient_phone?: string;
  recipient_telegram_id?: string;
  metadata?: Record<string, any>;
  created_at: string;
  sent_at?: string;
  delivered_at?: string;
  read_at?: string;
  error_message?: string;
  retry_count: number;
}

// Типы аналитики
export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface LeadConversionMetrics {
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
  avg_conversion_time?: number;
  conversion_by_source: Record<string, number>;
  conversion_by_status: Record<string, number>;
}

export interface RevenueMetrics {
  total_revenue: number;
  avg_deal_size: number;
  revenue_by_month: Record<string, number>;
  revenue_by_source: Record<string, number>;
  revenue_growth: number;
}

export interface PerformanceMetrics {
  response_time_avg: number;
  response_time_median: number;
  leads_per_day: number;
  deals_per_month: number;
  user_activity: Record<string, number>;
}

export interface DashboardData {
  lead_metrics: LeadConversionMetrics;
  revenue_metrics: RevenueMetrics;
  performance_metrics: PerformanceMetrics;
  recent_activities: Array<Record<string, any>>;
  top_performers: Array<Record<string, any>>;
}

export interface ChartData {
  labels: string[];
  datasets: Array<Record<string, any>>;
}

export interface AnalyticsData {
  dashboard: DashboardData;
  charts: Record<string, ChartData>;
  last_updated: string;
}

// Типы для форм
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirm_password: string;
  full_name?: string;
}

export interface LeadFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  position?: string;
  source: LeadSource;
  status: LeadStatus;
  notes?: string;
  budget?: number;
  timeline?: string;
}

// Типы для фильтров
export interface LeadFilter {
  status?: LeadStatus;
  source?: LeadSource;
  assigned_to?: number;
  created_after?: string;
  created_before?: string;
  search?: string;
}

export interface NotificationFilter {
  notification_type?: NotificationType;
  status?: NotificationStatus;
  priority?: NotificationPriority;
  recipient_email?: string;
  created_after?: string;
  created_before?: string;
}

export interface AnalyticsFilter {
  date_range?: DateRange;
  user_id?: number;
  lead_source?: string;
  lead_status?: string;
}

// Типы для пагинации
export interface PaginationParams {
  page: number;
  per_page: number;
}

export interface PaginatedData<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Типы для API
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiError {
  message: string;
  type: string;
  details?: any;
}

// Типы для состояния приложения
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Типы для компонентов
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export interface SelectProps extends BaseComponentProps {
  options: Array<{ value: string; label: string }>;
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
}

// Типы для событий
export interface LeadEvent {
  type: 'created' | 'updated' | 'deleted' | 'status_changed';
  lead: Lead;
  timestamp: string;
  user_id?: number;
}

export interface NotificationEvent {
  type: 'created' | 'sent' | 'delivered' | 'read';
  notification: Notification;
  timestamp: string;
}
