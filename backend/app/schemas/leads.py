"""
Pydantic схемы для лидов
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    """Статусы лидов"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(str, Enum):
    """Источники лидов"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PHONE = "phone"
    OTHER = "other"


class LeadBase(BaseModel):
    """Базовая схема лида"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    source: LeadSource = LeadSource.WEBSITE
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None


class LeadCreate(LeadBase):
    """Схема для создания лида"""
    pass


class LeadUpdate(BaseModel):
    """Схема для обновления лида"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    budget: Optional[float] = None
    timeline: Optional[str] = None


class LeadResponse(LeadBase):
    """Схема ответа с данными лида"""
    id: int
    amo_crm_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_to: Optional[int] = None

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Схема для списка лидов с пагинацией"""
    leads: List[LeadResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class LeadFilter(BaseModel):
    """Схема для фильтрации лидов"""
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    assigned_to: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None


class LeadStatistics(BaseModel):
    """Схема статистики по лидам"""
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    conversion_rate: float
    avg_response_time: Optional[float] = None
