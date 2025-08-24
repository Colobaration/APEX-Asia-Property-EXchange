# ⚡ Быстрая настройка CI/CD в GitHub

## 🎯 Что нужно сделать прямо сейчас

### 1. Откройте GitHub репозиторий
```
https://github.com/Colobaration/APEX-Asia-Property-EXchange
```

### 2. Настройте GitHub Secrets
Перейдите в **Settings** → **Secrets and variables** → **Actions**

Добавьте секреты:
```
DOMAIN=your-domain.com
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK (опционально)
```

### 3. Создайте Environments
Перейдите в **Settings** → **Environments**

#### Environment: `staging`
- **Protection rules**: 
  - ✅ Require a reviewer to approve new deployments
  - ✅ Restrict deployments to matching branches: `develop`
- **Environment variables**:
  - `ENVIRONMENT=staging`
  - `DOMAIN=staging.your-domain.com`

#### Environment: `production`
- **Protection rules**:
  - ✅ Require a reviewer to approve new deployments
  - ✅ Restrict deployments to matching branches: `main`
- **Environment variables**:
  - `ENVIRONMENT=production`
  - `DOMAIN=your-domain.com`

### 4. Настройте Branch Protection
Перейдите в **Settings** → **Branches**

#### Для ветки `main`:
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

#### Для ветки `develop`:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

### 5. Проверьте GitHub Actions
Перейдите в **Actions** и убедитесь, что:
- Запустился workflow `Simple CI/CD Pipeline`
- Все тесты прошли успешно
- Сборка Docker образов завершилась

## 🚀 Тестирование

### Сделайте тестовый push:
```bash
# Добавьте любой файл для тестирования
echo "# Test CI/CD" >> test-ci-cd.md
git add test-ci-cd.md
git commit -m "test: Тестирование CI/CD pipeline"
git push origin develop
```

### Проверьте результат:
1. Перейдите в **Actions** → **Simple CI/CD Pipeline**
2. Убедитесь, что все jobs прошли успешно
3. Проверьте, что образы опубликованы в **Packages**

## 📊 Ожидаемый результат

После настройки:
- ✅ При push в `develop` → автоматический деплой в staging
- ✅ При push в `main` → автоматический деплой в production
- ✅ При Pull Request → автоматическое тестирование
- ✅ Еженедельное сканирование безопасности

## 🆘 Если что-то не работает

### Проверьте:
1. **GitHub Actions** - есть ли ошибки в логах
2. **Secrets** - правильно ли настроены переменные
3. **Environments** - созданы ли окружения
4. **Branch protection** - настроены ли правила

### Полезные ссылки:
- **Actions**: https://github.com/Colobaration/APEX-Asia-Property-EXchange/actions
- **Settings**: https://github.com/Colobaration/APEX-Asia-Property-EXchange/settings
- **Packages**: https://github.com/Colobaration/APEX-Asia-Property-EXchange/packages

---

**Готово! Теперь у вас есть автоматический CI/CD! 🎉**
