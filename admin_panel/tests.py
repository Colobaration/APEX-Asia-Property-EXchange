from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from landings.models import Landing, LandingAnalytics
from integrations.models import APIIntegration, IntegrationLog
from logs.models import SystemLog, NotificationTemplate
from analytics.models import Dashboard, Metric, AnalyticsEvent
from django.utils import timezone
from datetime import date


class AdminPanelTestCase(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        # Создаем тестовые данные
        self.landing = Landing.objects.create(
            name='Тестовый лендинг',
            slug='test-landing',
            domain='https://test.example.com',
            status='active',
            created_by=self.user
        )
        
        self.integration = APIIntegration.objects.create(
            name='Тестовая интеграция',
            integration_type='amocrm',
            status='active',
            created_by=self.user
        )
        
        self.dashboard = Dashboard.objects.create(
            name='Тестовый дашборд',
            created_by=self.user
        )
        
        self.metric = Metric.objects.create(
            name='Тестовая метрика',
            metric_type='counter',
            data_source='landings',
            created_by=self.user
        )

    def test_admin_login(self):
        """Тест входа в админ-панель"""
        response = self.client.get(reverse('admin:login'))
        self.assertEqual(response.status_code, 200)
        
        # Тест успешного входа
        response = self.client.post(reverse('admin:login'), {
            'username': 'admin',
            'password': 'admin123',
        })
        self.assertEqual(response.status_code, 302)  # Редирект после входа
        
        # Проверяем, что мы вошли
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_landing_creation(self):
        """Тест создания лендинга"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin:landings_landing_add'), {
            'name': 'Новый лендинг',
            'slug': 'new-landing',
            'domain': 'https://new.example.com',
            'status': 'active',
            'theme': 'default',
            'created_by': self.admin_user.id,
        })
        self.assertEqual(response.status_code, 302)  # Редирект после создания
        
        # Проверяем, что лендинг создан
        landing = Landing.objects.get(slug='new-landing')
        self.assertEqual(landing.name, 'Новый лендинг')
        self.assertEqual(landing.status, 'active')

    def test_integration_creation(self):
        """Тест создания интеграции"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin:integrations_apiintegration_add'), {
            'name': 'Новая интеграция',
            'integration_type': 'whatsapp',
            'status': 'active',
            'auto_sync': True,
            'sync_interval': 3600,
            'created_by': self.admin_user.id,
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что интеграция создана
        integration = APIIntegration.objects.get(name='Новая интеграция')
        self.assertEqual(integration.integration_type, 'whatsapp')
        self.assertTrue(integration.auto_sync)

    def test_dashboard_creation(self):
        """Тест создания дашборда"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('admin:analytics_dashboard_add'), {
            'name': 'Новый дашборд',
            'description': 'Описание дашборда',
            'refresh_interval': 300,
            'is_public': True,
            'created_by': self.admin_user.id,
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что дашборд создан
        dashboard = Dashboard.objects.get(name='Новый дашборд')
        self.assertTrue(dashboard.is_public)
        self.assertEqual(dashboard.refresh_interval, 300)

    def test_landing_analytics(self):
        """Тест аналитики лендинга"""
        analytics = LandingAnalytics.objects.create(
            landing=self.landing,
            date=date.today(),
            visitors=100,
            unique_visitors=80,
            conversions=10,
            leads=5
        )
        
        # Проверяем конверсионную ставку
        conversion_rate = analytics.get_conversion_rate()
        self.assertEqual(conversion_rate, 10.0)  # 10/100 * 100 = 10%

    def test_integration_logging(self):
        """Тест логирования интеграций"""
        log = IntegrationLog.objects.create(
            integration=self.integration,
            level='INFO',
            message='Тестовое сообщение',
            data={'test': 'data'}
        )
        
        self.assertEqual(log.integration, self.integration)
        self.assertEqual(log.level, 'INFO')

    def test_system_logging(self):
        """Тест системного логирования"""
        log = SystemLog.log_info(
            source='test',
            message='Тестовое системное сообщение',
            user=self.user
        )
        
        self.assertEqual(log.source, 'test')
        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.user, self.user)

    def test_notification_template(self):
        """Тест шаблонов уведомлений"""
        template = NotificationTemplate.objects.create(
            name='Тестовый шаблон',
            template_type='email',
            subject='Привет {{name}}',
            content='Добро пожаловать, {{name}}!',
            variables={'name': 'string'},
            created_by=self.user
        )
        
        # Тест рендеринга шаблона
        context = {'name': 'Иван'}
        rendered_subject = template.render_subject(context)
        rendered_content = template.render_content(context)
        
        self.assertEqual(rendered_subject, 'Привет Иван')
        self.assertEqual(rendered_content, 'Добро пожаловать, Иван!')

    def test_analytics_event_tracking(self):
        """Тест отслеживания событий аналитики"""
        event = AnalyticsEvent.track_page_view(
            landing=self.landing,
            session_id='test-session-123',
            user_id='test-user-456'
        )
        
        self.assertEqual(event.event_type, 'page_view')
        self.assertEqual(event.landing, self.landing)
        self.assertEqual(event.session_id, 'test-session-123')

    def test_landing_url_generation(self):
        """Тест генерации URL лендинга с UTM метками"""
        self.landing.utm_source = 'google'
        self.landing.utm_medium = 'cpc'
        self.landing.utm_campaign = 'test-campaign'
        self.landing.save()
        
        full_url = self.landing.get_full_url()
        expected_url = 'https://test.example.com?utm_source=google&utm_medium=cpc&utm_campaign=test-campaign'
        self.assertEqual(full_url, expected_url)

    def test_integration_token_expiration(self):
        """Тест проверки истечения токена интеграции"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Токен не истек
        self.integration.expires_at = timezone.now() + timedelta(hours=1)
        self.integration.save()
        self.assertFalse(self.integration.is_token_expired())
        
        # Токен истек
        self.integration.expires_at = timezone.now() - timedelta(hours=1)
        self.integration.save()
        self.assertTrue(self.integration.is_token_expired())

    def test_admin_actions(self):
        """Тест админских действий"""
        self.client.force_login(self.admin_user)
        
        # Создаем несколько лендингов для тестирования массовых действий
        landing1 = Landing.objects.create(
            name='Лендинг 1',
            slug='landing-1',
            domain='https://landing1.example.com',
            status='inactive',
            created_by=self.admin_user
        )
        landing2 = Landing.objects.create(
            name='Лендинг 2',
            slug='landing-2',
            domain='https://landing2.example.com',
            status='inactive',
            created_by=self.admin_user
        )
        
        # Тест массовой активации
        response = self.client.post(reverse('admin:landings_landing_changelist'), {
            'action': 'activate_landings',
            '_selected_action': [landing1.id, landing2.id],
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что лендинги активированы
        landing1.refresh_from_db()
        landing2.refresh_from_db()
        self.assertEqual(landing1.status, 'active')
        self.assertEqual(landing2.status, 'active')

    def test_model_methods(self):
        """Тест методов моделей"""
        # Тест конфигурации лендинга
        self.landing.set_config_value('theme_color', '#ff0000')
        self.assertEqual(self.landing.get_config_value('theme_color'), '#ff0000')
        
        # Тест счетчиков интеграции
        self.integration.increment_sync_count()
        self.integration.increment_error_count('Тестовая ошибка')
        
        self.assertEqual(self.integration.sync_count, 1)
        self.assertEqual(self.integration.error_count, 1)
        self.assertEqual(self.integration.status, 'error')
        
        # Сброс ошибок
        self.integration.reset_error_count()
        self.assertEqual(self.integration.error_count, 0)
        self.assertEqual(self.integration.status, 'active')

    def test_admin_list_views(self):
        """Тест просмотра списков в админке"""
        self.client.force_login(self.admin_user)
        
        # Тест списка лендингов
        response = self.client.get(reverse('admin:landings_landing_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый лендинг')
        
        # Тест списка интеграций
        response = self.client.get(reverse('admin:integrations_apiintegration_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая интеграция')
        
        # Тест списка дашбордов
        response = self.client.get(reverse('admin:analytics_dashboard_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый дашборд')

    def test_admin_detail_views(self):
        """Тест детальных просмотров в админке"""
        self.client.force_login(self.admin_user)
        
        # Тест детального просмотра лендинга
        response = self.client.get(reverse('admin:landings_landing_change', args=[self.landing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый лендинг')
        
        # Тест детального просмотра интеграции
        response = self.client.get(reverse('admin:integrations_apiintegration_change', args=[self.integration.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая интеграция')

    def test_search_functionality(self):
        """Тест поиска в админке"""
        self.client.force_login(self.admin_user)
        
        # Тест поиска лендингов
        response = self.client.get(reverse('admin:landings_landing_changelist'), {
            'q': 'Тестовый'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый лендинг')
        
        # Тест поиска интеграций
        response = self.client.get(reverse('admin:integrations_apiintegration_changelist'), {
            'q': 'Тестовая'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая интеграция')

    def test_filter_functionality(self):
        """Тест фильтров в админке"""
        self.client.force_login(self.admin_user)
        
        # Тест фильтра по статусу лендингов
        response = self.client.get(reverse('admin:landings_landing_changelist'), {
            'status': 'active'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый лендинг')
        
        # Тест фильтра по типу интеграций
        response = self.client.get(reverse('admin:integrations_apiintegration_changelist'), {
            'integration_type': 'amocrm'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая интеграция')
