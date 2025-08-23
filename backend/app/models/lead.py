from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    
    # UTM метки
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_content = Column(String(100), nullable=True)
    utm_term = Column(String(100), nullable=True)
    
    # amoCRM интеграция
    amocrm_contact_id = Column(Integer, nullable=True)
    amocrm_lead_id = Column(Integer, nullable=True)
    
    # Статус и метаданные
    status = Column(String(50), default="new")
    source = Column(String(100), default="landing")
    
    # Финансовые данные
    cost = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    deals = relationship("Deal", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', phone='{self.phone}')>"
