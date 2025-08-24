/**
 * Компонент для защищенных роутов
 */

import React from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = [],
  fallback
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Показываем загрузку пока проверяем аутентификацию
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Если пользователь не аутентифицирован, перенаправляем на логин
  if (!isAuthenticated) {
    router.push('/login');
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Требуется авторизация
          </h2>
          <p className="text-gray-600">
            Перенаправление на страницу входа...
          </p>
        </div>
      </div>
    );
  }

  // Проверяем права доступа
  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.some(() => {
      // Здесь должна быть логика проверки прав пользователя
      // Пока просто проверяем, является ли пользователь суперпользователем
      return user.is_superuser;
    });

    if (!hasPermission) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">
              Доступ запрещен
            </h2>
            <p className="text-gray-600 mb-4">
              У вас недостаточно прав для доступа к этой странице
            </p>
            <button
              onClick={() => router.back()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Назад
            </button>
          </div>
        </div>
      );
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
