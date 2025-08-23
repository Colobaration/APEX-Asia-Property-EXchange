from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.lead import Lead
from app.models.deal import Deal
from app.core.logging import logger

class AnalyticsCalculator:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_cpl(self, start_date: datetime, end_date: datetime, utm_source: Optional[str] = None) -> Dict[str, Any]:
        """Расчет CPL (Cost Per Lead)"""
        try:
            # Базовый запрос для лидов
            query = self.db.query(Lead).filter(
                and_(
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date
                )
            )
            
            # Фильтр по UTM source если указан
            if utm_source:
                query = query.filter(Lead.utm_source == utm_source)
            
            # Получаем данные
            leads = query.all()
            total_leads = len(leads)
            
            # Здесь должна быть логика получения стоимости рекламы
            # Пока используем фиксированную стоимость для демонстрации
            total_cost = self._get_advertising_cost(start_date, end_date, utm_source)
            
            cpl = total_cost / total_leads if total_leads > 0 else 0
            
            # Разбивка по источникам
            breakdown = self._get_source_breakdown(start_date, end_date)
            
            return {
                "metric": "CPL",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "value": round(cpl, 2),
                "leads_count": total_leads,
                "total_cost": total_cost,
                "breakdown": breakdown
            }
            
        except Exception as e:
            logger.error(f"Error calculating CPL: {str(e)}")
            return {
                "metric": "CPL",
                "value": 0,
                "error": str(e)
            }
    
    def calculate_conversion_rate(self, start_date: datetime, end_date: datetime, pipeline_id: Optional[int] = None) -> Dict[str, Any]:
        """Расчет Conversion Rate"""
        try:
            # Общее количество лидов
            total_leads = self.db.query(Lead).filter(
                and_(
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date
                )
            ).count()
            
            # Количество завершенных сделок
            completed_deals = self.db.query(Deal).filter(
                and_(
                    Deal.created_at >= start_date,
                    Deal.created_at <= end_date,
                    Deal.status == "completed"
                )
            ).count()
            
            conversion_rate = (completed_deals / total_leads * 100) if total_leads > 0 else 0
            
            return {
                "metric": "Conversion Rate",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "value": round(conversion_rate, 2),
                "total_leads": total_leads,
                "completed_deals": completed_deals
            }
            
        except Exception as e:
            logger.error(f"Error calculating Conversion Rate: {str(e)}")
            return {
                "metric": "Conversion Rate",
                "value": 0,
                "error": str(e)
            }
    
    def calculate_roi(self, start_date: datetime, end_date: datetime, utm_source: Optional[str] = None) -> Dict[str, Any]:
        """Расчет ROI (Return on Investment)"""
        try:
            # Получаем доходы от сделок
            revenue_query = self.db.query(func.sum(Deal.amount)).filter(
                and_(
                    Deal.created_at >= start_date,
                    Deal.created_at <= end_date,
                    Deal.status == "completed"
                )
            )
            
            if utm_source:
                # Фильтруем по UTM source через связанные лиды
                revenue_query = revenue_query.join(Lead, Deal.lead_id == Lead.id).filter(Lead.utm_source == utm_source)
            
            total_revenue = revenue_query.scalar() or 0
            
            # Получаем затраты на рекламу
            total_cost = self._get_advertising_cost(start_date, end_date, utm_source)
            
            roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            return {
                "metric": "ROI",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "value": round(roi, 2),
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "profit": total_revenue - total_cost
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return {
                "metric": "ROI",
                "value": 0,
                "error": str(e)
            }
    
    def get_dashboard_data(self, period: str = "7d") -> Dict[str, Any]:
        """Получение данных для дашборда"""
        try:
            end_date = datetime.now()
            
            if period == "7d":
                start_date = end_date - timedelta(days=7)
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
            elif period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=7)
            
            # Рассчитываем все метрики
            cpl = self.calculate_cpl(start_date, end_date)
            cr = self.calculate_conversion_rate(start_date, end_date)
            roi = self.calculate_roi(start_date, end_date)
            
            # Статистика по источникам
            source_stats = self._get_source_statistics(start_date, end_date)
            
            return {
                "period": period,
                "metrics": {
                    "cpl": cpl,
                    "conversion_rate": cr,
                    "roi": roi
                },
                "source_statistics": source_stats,
                "recent_leads": self._get_recent_leads(10)
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _get_advertising_cost(self, start_date: datetime, end_date: datetime, utm_source: Optional[str] = None) -> float:
        """Получение стоимости рекламы (заглушка)"""
        # В реальном проекте здесь должна быть интеграция с рекламными платформами
        # Пока используем фиксированные значения для демонстрации
        
        base_cost = 1000  # Базовая стоимость в день
        
        days = (end_date - start_date).days
        total_cost = base_cost * days
        
        if utm_source:
            # Разные источники имеют разную стоимость
            source_costs = {
                "google": 1.2,
                "facebook": 0.8,
                "instagram": 0.9,
                "yandex": 1.1
            }
            multiplier = source_costs.get(utm_source, 1.0)
            total_cost *= multiplier
        
        return total_cost
    
    def _get_source_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Разбивка по источникам трафика"""
        try:
            sources = self.db.query(
                Lead.utm_source,
                func.count(Lead.id).label('count')
            ).filter(
                and_(
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date,
                    Lead.utm_source.isnot(None)
                )
            ).group_by(Lead.utm_source).all()
            
            breakdown = {}
            for source, count in sources:
                cost = self._get_advertising_cost(start_date, end_date, source)
                breakdown[source] = round(cost / count, 2) if count > 0 else 0
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting source breakdown: {str(e)}")
            return {}
    
    def _get_source_statistics(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Статистика по источникам"""
        try:
            stats = self.db.query(
                Lead.utm_source,
                func.count(Lead.id).label('leads_count'),
                func.avg(Deal.amount).label('avg_deal_amount')
            ).outerjoin(Deal, Lead.id == Deal.lead_id).filter(
                and_(
                    Lead.created_at >= start_date,
                    Lead.created_at <= end_date,
                    Lead.utm_source.isnot(None)
                )
            ).group_by(Lead.utm_source).all()
            
            return [
                {
                    "source": source,
                    "leads_count": count,
                    "avg_deal_amount": float(avg_amount) if avg_amount else 0
                }
                for source, count, avg_amount in stats
            ]
            
        except Exception as e:
            logger.error(f"Error getting source statistics: {str(e)}")
            return []
    
    def _get_recent_leads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних лидов"""
        try:
            leads = self.db.query(Lead).order_by(Lead.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": lead.id,
                    "name": lead.name,
                    "phone": lead.phone,
                    "email": lead.email,
                    "utm_source": lead.utm_source,
                    "status": lead.status,
                    "created_at": lead.created_at.isoformat()
                }
                for lead in leads
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent leads: {str(e)}")
            return []
