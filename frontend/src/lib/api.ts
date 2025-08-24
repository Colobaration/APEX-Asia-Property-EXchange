/**
 * Типизированный API клиент для APEX
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Типы для API ответов
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ApiError {
  message: string;
  type: string;
  details?: any;
}

// Конфигурация API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor для добавления токена
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor для обработки ошибок
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Токен истек, перенаправляем на логин
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private handleAuthError(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
  }

  // Методы для работы с аутентификацией
  async login(email: string, password: string): Promise<ApiResponse<{ access_token: string; user: any }>> {
    const response = await this.client.post('/api/auth/login', { email, password });
    return response.data;
  }

  async register(userData: any): Promise<ApiResponse<any>> {
    const response = await this.client.post('/api/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Методы для работы с лидами
  async getLeads(params?: any): Promise<PaginatedResponse<any>> {
    const response = await this.client.get('/api/leads', { params });
    return response.data;
  }

  async getLead(id: number): Promise<ApiResponse<any>> {
    const response = await this.client.get(`/api/leads/${id}`);
    return response.data;
  }

  async createLead(leadData: any): Promise<ApiResponse<any>> {
    const response = await this.client.post('/api/leads', leadData);
    return response.data;
  }

  async updateLead(id: number, leadData: any): Promise<ApiResponse<any>> {
    const response = await this.client.put(`/api/leads/${id}`, leadData);
    return response.data;
  }

  async deleteLead(id: number): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/api/leads/${id}`);
    return response.data;
  }

  // Методы для аналитики
  async getAnalytics(params?: any): Promise<ApiResponse<any>> {
    const response = await this.client.get('/api/analytics', { params });
    return response.data;
  }

  async getDashboardData(): Promise<ApiResponse<any>> {
    const response = await this.client.get('/api/analytics/dashboard');
    return response.data;
  }

  // Методы для уведомлений
  async getNotifications(params?: any): Promise<PaginatedResponse<any>> {
    const response = await this.client.get('/api/notifications', { params });
    return response.data;
  }

  async markNotificationAsRead(id: number): Promise<ApiResponse<void>> {
    const response = await this.client.patch(`/api/notifications/${id}/read`);
    return response.data;
  }

  // Методы для профиля пользователя
  async getProfile(): Promise<ApiResponse<any>> {
    const response = await this.client.get('/api/auth/profile');
    return response.data;
  }

  async updateProfile(userData: any): Promise<ApiResponse<any>> {
    const response = await this.client.put('/api/auth/profile', userData);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<any>> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Экспортируем единственный экземпляр
export const apiClient = new ApiClient();

// Хуки для React Query
export const apiHooks = {
  // Хуки для лидов
  useLeads: (params?: any) => ({
    queryKey: ['leads', params],
    queryFn: () => apiClient.getLeads(params),
  }),

  useLead: (id: number) => ({
    queryKey: ['lead', id],
    queryFn: () => apiClient.getLead(id),
    enabled: !!id,
  }),

  // Хуки для аналитики
  useAnalytics: (params?: any) => ({
    queryKey: ['analytics', params],
    queryFn: () => apiClient.getAnalytics(params),
  }),

  useDashboard: () => ({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboardData(),
  }),

  // Хуки для уведомлений
  useNotifications: (params?: any) => ({
    queryKey: ['notifications', params],
    queryFn: () => apiClient.getNotifications(params),
  }),

  // Хуки для профиля
  useProfile: () => ({
    queryKey: ['profile'],
    queryFn: () => apiClient.getProfile(),
  }),
};

// Утилиты для работы с API
export const apiUtils = {
  // Обработка ошибок API
  handleApiError: (error: AxiosError): ApiError => {
    const responseData = error.response?.data as any;
    if (responseData?.error) {
      return responseData.error;
    }
    return {
      message: error.message || 'Произошла ошибка',
      type: 'UnknownError',
    };
  },

  // Проверка статуса ответа
  isSuccessResponse: (response: any): boolean => {
    return response?.status === 'success' || response?.status === 200;
  },

  // Извлечение данных из ответа
  extractData: <T>(response: ApiResponse<T>): T => {
    return response.data;
  },
};
