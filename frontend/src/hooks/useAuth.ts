/**
 * Хук для управления аутентификацией
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import { User, LoginFormData, RegisterFormData } from '@/types';
import { apiClient } from '@/lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  const router = useRouter();

  // Проверяем токен при инициализации
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      // Проверяем наличие токена в localStorage
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
        return;
      }

      // Получаем профиль пользователя
      const response = await apiClient.getProfile();
      
      if (response.status === 'success') {
        setAuthState({
          user: response.data,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } else {
        // Токен недействителен
        localStorage.removeItem('auth_token');
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Ошибка проверки аутентификации'
      });
    }
  }, []);

  const login = useCallback(async (credentials: LoginFormData) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await apiClient.login(credentials.email, credentials.password);
      
      if (response.status === 'success') {
        // Сохраняем токен
        localStorage.setItem('auth_token', response.data.access_token);
        
        setAuthState({
          user: response.data.user,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });

        // Перенаправляем на главную страницу
        router.push('/dashboard');
        
        return { success: true };
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: response.message || 'Ошибка входа'
        }));
        return { success: false, error: response.message };
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || 'Ошибка входа';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, error: errorMessage };
    }
  }, [router]);

  const register = useCallback(async (userData: RegisterFormData) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await apiClient.register(userData);
      
      if (response.status === 'success') {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: null
        }));

        // После успешной регистрации перенаправляем на логин
        router.push('/login?message=registration_success');
        
        return { success: true };
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: response.message || 'Ошибка регистрации'
        }));
        return { success: false, error: response.message };
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || 'Ошибка регистрации';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, error: errorMessage };
    }
  }, [router]);

  const logout = useCallback(async () => {
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Очищаем состояние независимо от результата
      localStorage.removeItem('auth_token');
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      });
      
      // Перенаправляем на страницу входа
      router.push('/login');
    }
  }, [router]);

  const updateProfile = useCallback(async (userData: Partial<User>) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await apiClient.updateProfile(userData);
      
      if (response.status === 'success') {
        setAuthState(prev => ({
          ...prev,
          user: response.data,
          isLoading: false,
          error: null
        }));
        
        return { success: true };
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: response.message || 'Ошибка обновления профиля'
        }));
        return { success: false, error: response.message };
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || 'Ошибка обновления профиля';
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const clearError = useCallback(() => {
    setAuthState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    // Состояние
    user: authState.user,
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    error: authState.error,
    
    // Методы
    login,
    register,
    logout,
    updateProfile,
    checkAuth,
    clearError
  };
};
