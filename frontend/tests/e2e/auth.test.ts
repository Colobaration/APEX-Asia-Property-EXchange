/**
 * E2E тесты для аутентификации
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Переходим на страницу логина перед каждым тестом
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    // Проверяем, что форма логина отображается
    await expect(page.locator('h1')).toContainText('Вход в систему');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for invalid email', async ({ page }) => {
    // Вводим невалидный email
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Проверяем, что отображается ошибка валидации
    await expect(page.locator('.text-red-600')).toContainText('Неверный формат email');
  });

  test('should show validation errors for short password', async ({ page }) => {
    // Вводим короткий пароль
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', '123');
    await page.click('button[type="submit"]');

    // Проверяем, что отображается ошибка валидации
    await expect(page.locator('.text-red-600')).toContainText('Пароль должен содержать минимум 8 символов');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Мокаем неудачную попытку входа
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'error',
          message: 'Неверные учетные данные'
        })
      });
    });

    // Вводим данные и отправляем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Проверяем, что отображается ошибка
    await expect(page.locator('.text-red-600')).toContainText('Неверные учетные данные');
  });

  test('should successfully login and redirect to dashboard', async ({ page }) => {
    // Мокаем успешную попытку входа
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          data: {
            access_token: 'test_token',
            user: {
              id: 1,
              email: 'test@example.com',
              full_name: 'Test User'
            }
          }
        })
      });
    });

    // Мокаем получение профиля
    await page.route('**/api/auth/profile', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          data: {
            id: 1,
            email: 'test@example.com',
            full_name: 'Test User'
          }
        })
      });
    });

    // Вводим данные и отправляем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Проверяем, что произошло перенаправление на дашборд
    await expect(page).toHaveURL('/dashboard');
  });

  test('should navigate to registration page', async ({ page }) => {
    // Кликаем на ссылку регистрации
    await page.click('a[href="/register"]');

    // Проверяем, что перешли на страницу регистрации
    await expect(page).toHaveURL('/register');
    await expect(page.locator('h1')).toContainText('Регистрация');
  });
});

test.describe('Registration', () => {
  test.beforeEach(async ({ page }) => {
    // Переходим на страницу регистрации перед каждым тестом
    await page.goto('/register');
  });

  test('should display registration form', async ({ page }) => {
    // Проверяем, что форма регистрации отображается
    await expect(page.locator('h1')).toContainText('Регистрация');
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('input[name="confirm_password"]')).toBeVisible();
    await expect(page.locator('input[name="full_name"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for mismatched passwords', async ({ page }) => {
    // Вводим разные пароли
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirm_password"]', 'differentpassword');
    await page.fill('input[name="full_name"]', 'Test User');
    await page.click('button[type="submit"]');

    // Проверяем, что отображается ошибка валидации
    await expect(page.locator('.text-red-600')).toContainText('Пароли не совпадают');
  });

  test('should successfully register and redirect to login', async ({ page }) => {
    // Мокаем успешную регистрацию
    await page.route('**/api/auth/register', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          message: 'Регистрация успешна'
        })
      });
    });

    // Вводим данные и отправляем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirm_password"]', 'password123');
    await page.fill('input[name="full_name"]', 'Test User');
    await page.click('button[type="submit"]');

    // Проверяем, что произошло перенаправление на логин
    await expect(page).toHaveURL('/login?message=registration_success');
  });
});

test.describe('Protected Routes', () => {
  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Пытаемся перейти на защищенную страницу без аутентификации
    await page.goto('/dashboard');

    // Проверяем, что произошло перенаправление на логин
    await expect(page).toHaveURL('/login');
  });

  test('should access protected route when authenticated', async ({ page }) => {
    // Мокаем аутентификацию
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'test_token');
    });

    // Мокаем получение профиля
    await page.route('**/api/auth/profile', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          data: {
            id: 1,
            email: 'test@example.com',
            full_name: 'Test User'
          }
        })
      });
    });

    // Переходим на защищенную страницу
    await page.goto('/dashboard');

    // Проверяем, что страница загрузилась
    await expect(page.locator('h1')).toContainText('Дашборд');
  });
});

test.describe('Logout', () => {
  test('should logout and redirect to login', async ({ page }) => {
    // Мокаем аутентификацию
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'test_token');
    });

    // Мокаем получение профиля
    await page.route('**/api/auth/profile', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          data: {
            id: 1,
            email: 'test@example.com',
            full_name: 'Test User'
          }
        })
      });
    });

    // Переходим на дашборд
    await page.goto('/dashboard');

    // Кликаем на кнопку выхода
    await page.click('button[data-testid="logout-button"]');

    // Проверяем, что произошло перенаправление на логин
    await expect(page).toHaveURL('/login');

    // Проверяем, что токен удален из localStorage
    const token = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(token).toBeNull();
  });
});
