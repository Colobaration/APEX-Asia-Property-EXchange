from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    
    # amoCRM данные
    amocrm_deal_id = Column(Integer, nullable=False, unique=True)
    amocrm_pipeline_id = Column(Integer, nullable=True)
    amocrm_status_id = Column(Integer, nullable=True)
    
    # Финансовые данные
    amount = Column(Float, nullable=True)
    commission = Column(Float, default=0.0)
    commission_percent = Column(Float, default=0.0)
    
    # Статус сделки
    status = Column(String(50), default="new")
    stage = Column(String(100), nullable=True)
    
    # Дополнительные данные
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    lead = relationship("Lead", back_populates="deals")
    
    def __repr__(self):
        return f"<Deal(id={self.id}, amocrm_id={self.amocrm_deal_id}, amount={self.amount})>"
