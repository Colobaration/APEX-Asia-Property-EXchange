"""
Сервис для аналитики и отчетов
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from sqlalchemy.sql import extract

from app.models.lead import Lead
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsFilter,
    LeadConversionMetrics,
    RevenueMetrics,
    PerformanceMetrics,
    DashboardData,
    ChartData,
    AnalyticsResponse
)
from app.core.exceptions import ValidationError


class AnalyticsService:
    """Сервис для аналитики и отчетов"""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_data(self, user_id: Optional[int] = None) -> DashboardData:
        """Получение данных для дашборда"""
        lead_metrics = self.get_lead_conversion_metrics(user_id)
        revenue_metrics = self.get_revenue_metrics(user_id)
        performance_metrics = self.get_performance_metrics(user_id)
        recent_activities = self.get_recent_activities(user_id)
        top_performers = self.get_top_performers()

        return DashboardData(
            lead_metrics=lead_metrics,
            revenue_metrics=revenue_metrics,
            performance_metrics=performance_metrics,
            recent_activities=recent_activities,
            top_performers=top_performers
        )

    def get_lead_conversion_metrics(self, user_id: Optional[int] = None) -> LeadConversionMetrics:
        """Получение метрик конверсии лидов"""
        query = self.db.query(Lead)

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        total_leads = query.count()
        converted_leads = query.filter(Lead.status.in_(["qualified", "closed_won"])).count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0

        # Конверсия по источникам
        conversion_by_source = {}
        sources = self.db.query(Lead.source).distinct().all()
        for source in sources:
            source_count = query.filter(Lead.source == source[0]).count()
            conversion_by_source[source[0]] = source_count

        # Конверсия по статусам
        conversion_by_status = {}
        statuses = self.db.query(Lead.status).distinct().all()
        for status in statuses:
            status_count = query.filter(Lead.status == status[0]).count()
            conversion_by_status[status[0]] = status_count

        # Среднее время конверсии (упрощенный расчет)
        avg_conversion_time = None
        if converted_leads > 0:
            # Здесь можно добавить более сложную логику расчета времени конверсии
            pass

        return LeadConversionMetrics(
            total_leads=total_leads,
            converted_leads=converted_leads,
            conversion_rate=conversion_rate,
            avg_conversion_time=avg_conversion_time,
            conversion_by_source=conversion_by_source,
            conversion_by_status=conversion_by_status
        )

    def get_revenue_metrics(self, user_id: Optional[int] = None) -> RevenueMetrics:
        """Получение метрик выручки"""
        # Упрощенная реализация - в реальном проекте здесь была бы логика работы с сделками
        total_revenue = 0.0
        avg_deal_size = 0.0
        revenue_by_month = {}
        revenue_by_source = {}
        revenue_growth = 0.0

        # Заполняем тестовыми данными
        current_month = datetime.now().strftime("%Y-%m")
        revenue_by_month[current_month] = total_revenue

        return RevenueMetrics(
            total_revenue=total_revenue,
            avg_deal_size=avg_deal_size,
            revenue_by_month=revenue_by_month,
            revenue_by_source=revenue_by_source,
            revenue_growth=revenue_growth
        )

    def get_performance_metrics(self, user_id: Optional[int] = None) -> PerformanceMetrics:
        """Получение метрик производительности"""
        query = self.db.query(Lead)

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        # Количество лидов за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_leads = query.filter(Lead.created_at >= thirty_days_ago).count()
        leads_per_day = recent_leads / 30

        # Количество сделок за последний месяц (упрощенно)
        deals_per_month = query.filter(Lead.status == "closed_won").count()

        # Активность пользователей
        user_activity = {}
        if not user_id:
            # Получаем активность всех пользователей
            users = self.db.query(User).all()
            for user in users:
                user_leads = self.db.query(Lead).filter(Lead.assigned_to == user.id).count()
                user_activity[user.email] = user_leads

        # Упрощенные метрики времени ответа
        response_time_avg = 24.0  # часы
        response_time_median = 12.0  # часы

        return PerformanceMetrics(
            response_time_avg=response_time_avg,
            response_time_median=response_time_median,
            leads_per_day=leads_per_day,
            deals_per_month=deals_per_month,
            user_activity=user_activity
        )

    def get_recent_activities(self, user_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних активностей"""
        query = self.db.query(Lead)

        if user_id:
            query = query.filter(Lead.assigned_to == user_id)

        recent_leads = (
            query.order_by(desc(Lead.created_at))
            .limit(limit)
            .all()
        )

        activities = []
        for lead in recent_leads:
            activities.append({
                "id": lead.id,
                "type": "lead_created",
                "title": f"Новый лид: {lead.first_name} {lead.last_name}",
                "description": f"Email: {lead.email}, Источник: {lead.source}",
                "timestamp": lead.created_at.isoformat(),
                "user_id": lead.assigned_to,
                "metadata": {
                    "lead_id": lead.id,
                    "status": lead.status,
                    "source": lead.source
                }
            })

        return activities

    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Получение топ-исполнителей"""
        # Подсчитываем количество лидов по пользователям
        user_stats = (
            self.db.query(
                User.id,
                User.email,
                User.full_name,
                func.count(Lead.id).label('total_leads'),
                func.count(Lead.id).filter(Lead.status == "closed_won").label('converted_leads')
            )
            .outerjoin(Lead, User.id == Lead.assigned_to)
            .group_by(User.id, User.email, User.full_name)
            .order_by(desc('converted_leads'))
            .limit(limit)
            .all()
        )

        performers = []
        for stat in user_stats:
            conversion_rate = (stat.converted_leads / stat.total_leads * 100) if stat.total_leads > 0 else 0
            performers.append({
                "user_id": stat.id,
                "email": stat.email,
                "full_name": stat.full_name,
                "total_leads": stat.total_leads,
                "converted_leads": stat.converted_leads,
                "conversion_rate": conversion_rate
            })

        return performers

    def get_chart_data(self, chart_type: str, filters: Optional[AnalyticsFilter] = None) -> ChartData:
        """Получение данных для графиков"""
        if chart_type == "leads_by_source":
            return self._get_leads_by_source_chart(filters)
        elif chart_type == "leads_by_status":
            return self._get_leads_by_status_chart(filters)
        elif chart_type == "leads_timeline":
            return self._get_leads_timeline_chart(filters)
        elif chart_type == "conversion_funnel":
            return self._get_conversion_funnel_chart(filters)
        else:
            raise ValidationError(f"Неизвестный тип графика: {chart_type}")

    def _get_leads_by_source_chart(self, filters: Optional[AnalyticsFilter] = None) -> ChartData:
        """График лидов по источникам"""
        query = self.db.query(Lead)

        if filters and filters.user_id:
            query = query.filter(Lead.assigned_to == filters.user_id)

        source_stats = (
            query.with_entities(
                Lead.source,
                func.count(Lead.id).label('count')
            )
            .group_by(Lead.source)
            .all()
        )

        labels = [stat.source for stat in source_stats]
        data = [stat.count for stat in source_stats]

        return ChartData(
            labels=labels,
            datasets=[{
                "label": "Количество лидов",
                "data": data,
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"
                ]
            }]
        )

    def _get_leads_by_status_chart(self, filters: Optional[AnalyticsFilter] = None) -> ChartData:
        """График лидов по статусам"""
        query = self.db.query(Lead)

        if filters and filters.user_id:
            query = query.filter(Lead.assigned_to == filters.user_id)

        status_stats = (
            query.with_entities(
                Lead.status,
                func.count(Lead.id).label('count')
            )
            .group_by(Lead.status)
            .all()
        )

        labels = [stat.status for stat in status_stats]
        data = [stat.count for stat in status_stats]

        return ChartData(
            labels=labels,
            datasets=[{
                "label": "Количество лидов",
                "data": data,
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"
                ]
            }]
        )

    def _get_leads_timeline_chart(self, filters: Optional[AnalyticsFilter] = None) -> ChartData:
        """График лидов по времени"""
        query = self.db.query(Lead)

        if filters and filters.user_id:
            query = query.filter(Lead.assigned_to == filters.user_id)

        # Группируем по дням за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        timeline_stats = (
            query.filter(Lead.created_at >= thirty_days_ago)
            .with_entities(
                func.date(Lead.created_at).label('date'),
                func.count(Lead.id).label('count')
            )
            .group_by(func.date(Lead.created_at))
            .order_by(func.date(Lead.created_at))
            .all()
        )

        labels = [stat.date.strftime("%Y-%m-%d") for stat in timeline_stats]
        data = [stat.count for stat in timeline_stats]

        return ChartData(
            labels=labels,
            datasets=[{
                "label": "Новые лиды",
                "data": data,
                "borderColor": "#36A2EB",
                "backgroundColor": "rgba(54, 162, 235, 0.1)",
                "fill": True
            }]
        )

    def _get_conversion_funnel_chart(self, filters: Optional[AnalyticsFilter] = None) -> ChartData:
        """График воронки конверсии"""
        query = self.db.query(Lead)

        if filters and filters.user_id:
            query = query.filter(Lead.assigned_to == filters.user_id)

        # Подсчитываем количество лидов на каждом этапе
        stages = ["new", "contacted", "qualified", "proposal", "negotiation", "closed_won"]
        stage_counts = []

        for stage in stages:
            count = query.filter(Lead.status == stage).count()
            stage_counts.append(count)

        return ChartData(
            labels=stages,
            datasets=[{
                "label": "Количество лидов",
                "data": stage_counts,
                "backgroundColor": [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"
                ]
            }]
        )

    def get_analytics_response(self, filters: Optional[AnalyticsFilter] = None) -> AnalyticsResponse:
        """Получение полного ответа с аналитическими данными"""
        dashboard = self.get_dashboard_data(filters.user_id if filters else None)
        
        charts = {
            "leads_by_source": self._get_leads_by_source_chart(filters),
            "leads_by_status": self._get_leads_by_status_chart(filters),
            "leads_timeline": self._get_leads_timeline_chart(filters),
            "conversion_funnel": self._get_conversion_funnel_chart(filters)
        }

        return AnalyticsResponse(
            dashboard=dashboard,
            charts=charts,
            last_updated=datetime.utcnow()
        )
