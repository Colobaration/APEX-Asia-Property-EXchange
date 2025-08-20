from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
from app.core.db import get_db
from app.models.lead import Lead
from app.models.deal import Deal
from app.analytics.metrics import AnalyticsCalculator

router = APIRouter()

@router.get("/cpl")
async def get_cpl(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    utm_source: Optional[str] = Query(None, description="UTM source filter"),
    db: Session = Depends(get_db)
):
    """
    Получение CPL (Cost Per Lead) метрик
    """
    try:
        calculator = AnalyticsCalculator(db)
        
        # Парсинг дат
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        
        cpl_data = await calculator.calculate_cpl(
            start_date=start,
            end_date=end,
            utm_source=utm_source
        )
        
        return {
            "metric": "CPL",
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "value": cpl_data["cpl"],
            "leads_count": cpl_data["leads_count"],
            "total_cost": cpl_data["total_cost"],
            "breakdown": cpl_data["breakdown"]
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/cr")
async def get_conversion_rate(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    pipeline_id: Optional[int] = Query(None, description="Pipeline ID"),
    db: Session = Depends(get_db)
):
    """
    Получение Conversion Rate метрик
    """
    try:
        calculator = AnalyticsCalculator(db)
        
        # Парсинг дат
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        
        cr_data = await calculator.calculate_conversion_rate(
            start_date=start,
            end_date=end,
            pipeline_id=pipeline_id
        )
        
        return {
            "metric": "Conversion Rate",
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "value": cr_data["conversion_rate"],
            "leads_count": cr_data["leads_count"],
            "deals_count": cr_data["deals_count"],
            "pipeline_breakdown": cr_data["pipeline_breakdown"]
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/roi")
async def get_roi(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    utm_source: Optional[str] = Query(None, description="UTM source filter"),
    db: Session = Depends(get_db)
):
    """
    Получение ROI (Return on Investment) метрик
    """
    try:
        calculator = AnalyticsCalculator(db)
        
        # Парсинг дат
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=30)
        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        
        roi_data = await calculator.calculate_roi(
            start_date=start,
            end_date=end,
            utm_source=utm_source
        )
        
        return {
            "metric": "ROI",
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "value": roi_data["roi"],
            "revenue": roi_data["revenue"],
            "cost": roi_data["cost"],
            "profit": roi_data["profit"],
            "breakdown": roi_data["breakdown"]
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/dashboard")
async def get_dashboard_data(
    period: str = Query("30d", description="Period: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Получение данных для дашборда
    """
    try:
        calculator = AnalyticsCalculator(db)
        
        # Определение периода
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period, 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        dashboard_data = await calculator.get_dashboard_data(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "period": period,
            "metrics": dashboard_data["metrics"],
            "charts": dashboard_data["charts"],
            "top_sources": dashboard_data["top_sources"],
            "recent_leads": dashboard_data["recent_leads"]
        }
        
    except Exception as e:
        return {"error": str(e)}
