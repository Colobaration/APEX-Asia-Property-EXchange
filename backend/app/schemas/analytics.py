"""
Pydantic схемы для аналитики
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class DateRange(BaseModel):
    """Диапазон дат для аналитики"""
    start_date: date
    end_date: date


class AnalyticsFilter(BaseModel):
    """Фильтр для аналитических запросов"""
    date_range: Optional[DateRange] = None
    user_id: Optional[int] = None
    lead_source: Optional[str] = None
    lead_status: Optional[str] = None


class LeadConversionMetrics(BaseModel):
    """Метрики конверсии лидов"""
    total_leads: int
    converted_leads: int
    conversion_rate: float
    avg_conversion_time: Optional[float] = None
    conversion_by_source: Dict[str, int]
    conversion_by_status: Dict[str, int]


class RevenueMetrics(BaseModel):
    """Метрики выручки"""
    total_revenue: float
    avg_deal_size: float
    revenue_by_month: Dict[str, float]
    revenue_by_source: Dict[str, float]
    revenue_growth: float


class PerformanceMetrics(BaseModel):
    """Метрики производительности"""
    response_time_avg: float
    response_time_median: float
    leads_per_day: float
    deals_per_month: float
    user_activity: Dict[str, int]


class DashboardData(BaseModel):
    """Данные для дашборда"""
    lead_metrics: LeadConversionMetrics
    revenue_metrics: RevenueMetrics
    performance_metrics: PerformanceMetrics
    recent_activities: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]


class ChartData(BaseModel):
    """Данные для графиков"""
    labels: List[str]
    datasets: List[Dict[str, Any]]


class AnalyticsResponse(BaseModel):
    """Ответ с аналитическими данными"""
    dashboard: DashboardData
    charts: Dict[str, ChartData]
    last_updated: datetime
