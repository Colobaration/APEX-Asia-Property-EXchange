from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="APEX Asia Property Exchange API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}

@app.get("/")
async def root():
    return {"message": "APEX Asia Property Exchange API"}

# Здесь будут импортированы и подключены остальные роутеры
# from app.api import auth, leads, analytics, notifications, webhooks
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
# app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
# app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
