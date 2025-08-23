from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import leads, auth, webhooks, analytics, notifications

app = FastAPI(
    title="Asia Deals CRM API",
    description="API для интеграции с amoCRM и аналитики",
    version="1.0.0"
)

# CORS middleware - безопасные настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts if not settings.debug else ["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Asia Deals CRM API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
